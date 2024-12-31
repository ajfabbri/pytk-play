#!/usr/bin/env python
import tkinter as tk
from tkinter import ttk
import threading
import time

import sound
from sound import Sound

class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.createWidgets()

        # timer state
        self.started_timer = False
        self.pack()

        # sound engine
        self.sound = sound.Sound()
        self.sound.play(sound.Samples.STARTUP)

    def createWidgets(self):

        style = ttk.Style(self)
        # dark mode settings
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="black", foreground="white")
        style.configure("TLabel", padding=6, relief="flat", background="black", foreground="white")
        style.configure("TFrame", padding=6, relief="flat", background="black", foreground="white")
        style.configure("TLabel", padding=6, relief="flat", background="black", foreground="white")

        # style for large-text clock label
        style.configure("TLabel.Large", padding=6, relief="flat", background="black", foreground="white", font=("Helvetica", 44, "bold"))
        style.layout("TLabel.Large", [('Label.border', {'sticky': 'nswe',
            'border': '1', 'children': [('Label.padding', {'sticky': 'nswe',
            'children': [('Label.label', {'sticky': 'nswe'})]})]})])

        #filename = "img\\tomato-pixel.jpg"
        filename = "img\\tomato-pixel.png"
        img = tk.PhotoImage(width=400, height=400, file=filename)
        self.logo = ttk.Label(self, image=img)
        self.logo.pack()

        self.armButton = ttk.Button(self, text='Start',
            command=self.arm)
        self.armButton.pack()

        self.timeLabel = ttk.Label(self, text="OO:OO", style="TLabel.Large")
        self.timeLabel.pack()

        self.quitButton = ttk.Button(self, text='Quit',
            command=self.quit)
        self.quitButton.pack()

    # for Timer to update the time display
    def setTimeText(self, text: str):
        self.timeLabel.config(text=text)

    # for Timer to notify us when expired
    def onTimerExpired(self):
        self.sound.play(sound.Samples.TIMER_EXPIRED2)
        time.sleep(1.2)
        self.sound.play(sound.Samples.TIMER_EXPIRED1)
        self.started_timer = False

    def arm(self, secs=8):
        if self.started_timer:
            print("ignoring arm butt: timer already started")
            self.sound.play(sound.Samples.TIMER_STOP)
            return

        print(f"Starting {secs} second timer")
        self.timer = MyTimer(self)
        self.timer.start(secs)
        self.started_timer = True

    def quit(self):
        self.sound.play(sound.Samples.SHUTDOWN)
        time.sleep(0.3)
        super().quit()

    def destroy(self):
        self.sound.play(sound.Samples.ABRUPT_SHUTDOWN)
        time.sleep(0.5)
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

    def run(self):
        while True:
            time.sleep(1.0)
            now = time.time()
            elapsed = now - self.start_time
            secs_left = self.duration - elapsed
            if secs_left <= 0:
                self.app.setTimeText("00:00")
                self.app.onTimerExpired()
                print("Timer expired, exiting timer loop")
                break
            whole_mins = int(secs_left) / 60
            mins = float(whole_mins)
            secs = int(secs_left) % 60
            self.app.setTimeText(f"{mins:02.0f}:{secs:02.0f}")

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