#!/usr/bin/env python
import tkinter as tk
from tkinter import ttk
import threading
import time

import sound
from sound import Sound

class Application(ttk.Frame):
    # parameters
    pom_secs = 25 * 60
    short_break_secs = 5 * 60
    long_break_secs = 15 * 60
        
    def __init__(self, master=None):
        # timer state
        self.timer = MyTimer(self)
        self.started_timer = False

        super().__init__(master)
        self.createWidgets()

        # sound engine
        self.sound = sound.Sound()
        self.sound.play(sound.Samples.STARTUP)

    def createWidgets(self):
        # dark mode settings
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="black", foreground="white")
        style.configure("TLabel", padding=6, relief="flat", background="black", foreground="white")
        style.configure("TFrame", padding=6, relief="flat", background="black", foreground="white")
        style.configure("TLabel", padding=6, relief="flat", background="black", foreground="white")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        main_tab = ttk.Frame(self.notebook)
        config_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="Pomodoro Timer")
        self.notebook.add(config_tab, text="Settings")
        # select main tab by default, allow switching to config and back
        self.notebook.select(main_tab)
        
        self.createMainTab(main_tab, style)
        self.createConfigTab(config_tab, style)
        self.pack()

    def createMainTab(self, tab: ttk.Frame, style: ttk.Style):
        # style for large-text clock label
        style.configure("TLabel.Large", padding=6, relief="flat", background="black", foreground="white", font=("Helvetica", 36))
        style.layout("TLabel.Large", [('Label.border', {'sticky': 'nswe',
            'border': '1', 'children': [('Label.padding', {'sticky': 'nswe',
            'children': [('Label.label', {'sticky': 'nswe'})]})]})])

        #filename = "img\\tomato-pixel.jpg"
        filename = "img\\tomato-pixel.png"
        img = tk.PhotoImage(width=400, height=400, file=filename)
        self.logo = ttk.Label(tab, image=img)
        self.logo.pack()

        self.armButton = ttk.Button(tab, text='Start',
            command=self.arm)
        self.armButton.pack()

        self.timeLabel = ttk.Label(tab, text="--:--", style="TLabel.Large")
        self.timeLabel.pack()

        style.configure("TProgressbar", padding=6, relief="flat", background="black", foreground="#aaaaff")
        self.progress = ttk.Progressbar(tab, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(fill="x")
        self.quitButton = ttk.Button(tab, text='Quit',
            command=self.quit)
        self.quitButton.pack()

    def createConfigTab(self, tab: ttk.Frame, style: ttk.Style):
        style.configure("TLabel.Large", padding=6, relief="flat", background="black", foreground="white", font=("Helvetica", 36))
        style.layout("TLabel.Large", [('Label.border', {'sticky': 'nswe',
            'border': '1', 'children': [('Label.padding', {'sticky': 'nswe',
            'children': [('Label.label', {'sticky': 'nswe'})]})]})])

        self.pomMinsLabel = ttk.Label(tab, text="Pomodoro Duration (mins):")
        self.pomMinsLabel.pack()

        self.pomMinsEntry = ttk.Entry(tab)
        self.pomMinsEntry.pack()

        self.shortBreakMinsLabel = ttk.Label(tab, text="Short Break Duration (mins):")
        self.shortBreakMinsLabel.pack()

        self.shortBreakMinsEntry = ttk.Entry(tab, text=str(self.short_break_secs // 60))
        self.shortBreakMinsEntry.pack()

        self.longBreakMinsLabel = ttk.Label(tab, text="Long Break Duration (mins):")
        self.longBreakMinsLabel.pack()

        self.longBreakMinsEntry = ttk.Entry(tab)
        self.longBreakMinsEntry.pack()

        self.saveButton = ttk.Button(tab, text='Save',
            command=self.saveConfig)
        self.saveButton.pack()

    def saveConfig(self):
        if self.pomMinsEntry.get().isnumeric():
            self.pom_secs = int(self.pomMinsEntry.get()) * 60
        if self.shortBreakMinsEntry.get().isnumeric():
            self.short_break_secs = int(self.shortBreakMinsEntry.get()) * 60
        if self.longBreakMinsEntry.get().isnumeric():
            self.long_break_secs = int(self.longBreakMinsEntry.get()) * 60
        print(f"Saved config: pom={self.pom_secs}, short={self.short_break_secs}, long={self.long_break_secs}")

    # for Timer to update the time display
    def setTimeText(self, text: str):
        self.timeLabel.config(text=text)

    # for Timer to notify us when expired
    def onTimerExpired(self):
        self.sound.play(sound.Samples.TIMER_EXPIRED2)
        time.sleep(1.2)
        self.sound.play(sound.Samples.TIMER_EXPIRED1)
        self.started_timer = False

    def arm(self):
        if self.started_timer:
            print("ignoring arm butt: timer already started")
            self.sound.play(sound.Samples.TIMER_STOP)
            return

        print(f"Starting {self.pom_secs} second timer")
        self.sound.play(sound.Samples.TIMER_START)
        self.timer.start(self.pom_secs)
        self.started_timer = True

    def quit(self):
        self.sound.play(sound.Samples.SHUTDOWN)
        self.timer.stop()
        time.sleep(0.3)
        super().quit()

    def destroy(self):
        self.sound.play(sound.Samples.ABRUPT_SHUTDOWN)
        self.timer.stop()
        time.sleep(0.1)
        super().destroy()

class MyTimer(threading.Thread):
    def __init__(self, app: Application):
        print("debug: MyTimer init")
        self.app = app
        self.started = False
        threading.Thread.__init__(self)

    def start(self, seconds: int):
        if self.started:
            print("Timer already started, ignoring start()")
            return
        print("debug: timer started")
        self.duration = seconds
        self.started = True
        self.start_time = time.time()

        # we need to actually call the underlying Thread.start()
        super().start()

    def stop(self):
        self.started = False

    def run(self):
        while self.started:
            now = time.time()
            elapsed = now - self.start_time
            secs_left = self.duration - elapsed
            if secs_left <= 0:
                self.app.setTimeText("00:00")
                self.app.onTimerExpired()
                print("Timer expired, exiting timer loop")
                break
            whole_mins = int(secs_left) // 60
            mins = float(whole_mins)
            secs = int(secs_left) % 60
            self.app.setTimeText(f"{mins:02.0f}:{secs:02.0f}")
            self.app.progress["value"] = 100 * (1 - secs_left / self.duration)
            time.sleep(0.5)

# main
app = Application()
app.master.title('Pomodoro Timer')
app.master.maxsize(400, 400)

# handle shudwoen to play exit sound
def on_closing():
    app.destroy()
    tk.Tk().quit()

app.master.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()