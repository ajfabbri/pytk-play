#!/usr/bin/env python
import tkinter as tk
import threading
import time

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

        # timer state
        self.started_timer = False

    # 2x2 grid
    def createWidgets(self):
        self.armButton = tk.Button(self, text='Start',
            command=self.arm)
        self.armButton.grid(row=0, column=0, padx=10, pady=10)

        self.timeLabel = tk.Label(self, text="OO:OO")
        self.timeLabel.grid(row=0, column=1)

        self.quitButton = tk.Button(self, text='Quit',
            command=self.quit)
        self.quitButton.grid(column=1, row=1)

    def setTimeText(self, text: str):
        self.timeLabel.config(text=text)

    def arm(self, secs=120):
        if self.started_timer:
            print("ignoring arm butt: timer already started")
            return

        print(f"Starting {secs} second timer")
        self.timer = MyTimer(self)
        self.timer.start(secs)

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
                print("Timer expired, exiting timer loop")
                break
            whole_mins = int(secs_left) / 60
            mins = float(whole_mins)
            secs = int(secs_left) % 60
            self.app.setTimeText(f"{mins:2.0f}:{secs:2.0f}")

app = Application()
app.master.title('Sample application')
app.mainloop()