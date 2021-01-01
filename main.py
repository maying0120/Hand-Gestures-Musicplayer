import math
from tkinter import font as tkFont
import numpy as np
import cv2  # required 3+
import tkinter as tk
from threading import Thread
import queue as Queue
import time
from pygame import mixer
import os

import GestureMusic.GestureMusic.player as player


class MusicPlayer:

    # __all__ = ['play', 'pause', 'unpause', 'move_prev', 'move_next', 'vol_up', 'vol_down', 'playjay', 'exit']

    def __init__(self):
        self.volumn = 0.2

    @staticmethod
    def play():
        player.playsong()

    @staticmethod
    def pause():
        player.stopsong()

    @staticmethod
    def unpause():
        player.consong()

    @staticmethod
    def move_next():
        player.nextsong()

    @staticmethod
    def move_prev():
        player.previoussong()

    def vol_up(self):
        # check_call(['vlc-ctrl', 'volume', '+0.1'])
        # up()
        self.volumn += 0.1
        mixer.music.set_volume(self.volumn)

    def vol_down(self):
        # check_call(['vlc-ctrl', 'volume', '-0.1'])
        self.volumn -= 0.1
        mixer.music.set_volume(self.volumn)

    @staticmethod
    def playjay():
        player.playjay()

    @staticmethod
    def exit():
        os.kill(os.getpid(), 9)
        # sys.exit(1)

    @staticmethod
    def get_current_song():
        return player.get_cur_song()

    def get_current_volume(self):
        return self.volumn


request_queue = Queue.Queue()
result_queue = Queue.Queue()
t = None
debug = False
enable_commands = False
REALLY_NOT_DEBUG = True
CHANGE_VOLUME = False
COOLDOWN = 5
LAST_TIME = time.time()


def submit_to_tkinter(cb, *args, **kwargs):
    request_queue.put((cb, args, kwargs))
    return result_queue.get()


def debug_toggle():
    global debug
    debug = not debug


def toggle_commands():
    global enable_commands
    enable_commands = not enable_commands


def main_tk_thread():
    global t

    def timertick():
        try:
            cb, args, kwargs = request_queue.get_nowait()
        except Queue.Empty:
            pass
        else:  # if no exception was raised
            retval = cb(*args, **kwargs)
            result_queue.put(retval)
        # reschedule after some time
        t.after(10, timertick)

    # create main Tk window
    t = tk.Tk()
    t.title("Controller")
    t.geometry('%dx%d+%d+%d' % (520, 320, 850, 200))
    # set font for labels
    font = tkFont.Font(family="Arial", size=18, weight=tkFont.BOLD)
    defects = tk.Label(t, name="defects", text="None", font=font)
    defects.place(x=20, y=10)
    command = tk.Label(t, name="command", text="None", font=font)
    command.place(x=20, y=60)
    song = tk.Label(t, name="song", text="None", font=font)
    song.place(x=20, y=110)
    volume = tk.Label(t, name="volume", text="None", font=font)
    volume.place(x=20, y=160)
    # start timer a.k.a. scheduler
    timertick()
    # main Tk loop
    t.mainloop()


# setters for Tk GUI elements
def get_defects(a):
    t.children["defects"].configure(text=str("defects = %s " % a))


def get_command(a):
    t.children["command"].configure(text=str("command = %s " % a))


def get_song(a):
    t.children["song"].configure(text=str("Current Song = %s " % a))


def get_volume(a):
    t.children["volume"].configure(text=str("Current Volume = %s " % a))


def check_command(c):
    mp = MusicPlayer()
    submit_to_tkinter(get_defects, str(c))
    if c == 11:
        if REALLY_NOT_DEBUG:
            mp.play()
        return "PLAY", mp.get_current_song(), mp.get_current_volume()
    elif c == 8:
        if REALLY_NOT_DEBUG:
            mp.pause()
        return "PAUSE", mp.get_current_song(), mp.get_current_volume()

    elif c == 10:
        if REALLY_NOT_DEBUG:
            mp.unpause()
        return "UNPAUSE", mp.get_current_song(), mp.get_current_volume()

    elif c == 3:
        if REALLY_NOT_DEBUG:
            mp.move_next()
        return "NEXT", mp.get_current_song(), mp.get_current_volume()
    elif c == 4:
        if REALLY_NOT_DEBUG:
            mp.move_prev()
        return "PREVIOUS", mp.get_current_song(), mp.get_current_volume()
    elif c == 0:
        mp.vol_down()
        return "VOLUME CONTROL DOWN", mp.get_current_song(), mp.get_current_volume()
    elif c == 1:
        mp.vol_up()
        return "VOLUME CONTROL UP", mp.get_current_song(), mp.get_current_volume()
    elif c == 2:
        mp.playjay()
        return "PLAY JAY CHOU'S SONGS", mp.get_current_song(), mp.get_current_volume()
    elif c == 5:
        mp.exit()

    return None


if __name__ == '__main__':
    mp = MusicPlayer()
    t = Thread(target=main_tk_thread, daemon=True)
    t.start()

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        try:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            kernel = np.ones((3, 3), np.uint8)

            # define region of interest
            roi = frame[100:300, 100:300]

            cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 0), 0)
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # define range of skin color in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)

            # extract skin colur imagw
            mask = cv2.inRange(hsv, lower_skin, upper_skin)

            # extrapolate the hand to fill dark spots within
            mask = cv2.dilate(mask, kernel, iterations=4)

            # blur the image
            mask = cv2.GaussianBlur(mask, (5, 5), 100)

            # find contours
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # find contour of max area(hand)
            cnt = max(contours, key=lambda x: cv2.contourArea(x))

            # approx the contour a little
            epsilon = 0.0005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            # make convex hull around hand
            hull = cv2.convexHull(cnt)

            # define area of hull and area of hand
            areahull = cv2.contourArea(hull)
            areacnt = cv2.contourArea(cnt)

            # find the percentage of area not covered by hand in convex hull
            arearatio = ((areahull - areacnt) / areacnt) * 100

            # find the defects in convex hull with respect to hand
            hull = cv2.convexHull(approx, returnPoints=False)
            defects = cv2.convexityDefects(approx, hull)

            # l = no. of defects
            l = 0

            # code for finding no. of defects due to fingers
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(approx[s][0])
                end = tuple(approx[e][0])
                far = tuple(approx[f][0])
                pt = (100, 180)

                # find length of all sides of triangle
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                s = (a + b + c) / 2
                ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

                # distance between point and convex hull
                d = (2 * ar) / a

                # apply cosine rule here
                angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                # ignore angles > 90 and ignore points very close to convex hull(they generally come due to noise)
                if angle <= 90 and d > 30:
                    l += 1
                    cv2.circle(roi, far, 3, [255, 0, 0], -1)

                # draw lines around hand
                cv2.line(roi, start, end, [0, 255, 0], 2)

            l += 1

            # print corresponding gestures which are in their ranges
            font = cv2.FONT_HERSHEY_SIMPLEX
            if l == 1:
                if areacnt < 2000:
                    cv2.putText(frame, 'Put hand in the box', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    temp = -1
                else:
                    if arearatio < 12:
                        cv2.putText(frame, '0', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        temp = 0
                    elif arearatio < 17.5:
                        cv2.putText(frame, 'Good', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        temp = 10
                    elif arearatio < 30:
                        cv2.putText(frame, 'Good', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        print('arearatio1', arearatio)
                        temp = 1
                    else:
                        cv2.putText(frame, '1', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        temp = 6

            elif l == 2:

                if arearatio < 15:
                    cv2.putText(frame, '9', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    print('arearatio9', arearatio)
                    temp = 9

                if 15 < arearatio < 34:
                    cv2.putText(frame, '2', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    temp = 2

                else:
                    cv2.putText(frame, '8', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    temp = 8

            elif l == 3:

                if arearatio < 27:
                    cv2.putText(frame, '3', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    temp = 3
                else:
                    cv2.putText(frame, 'ok', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    temp = 11

            elif l == 4:
                cv2.putText(frame, '4', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                temp = 4

            elif l == 5:
                cv2.putText(frame, '5', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
                temp = 5

            elif l == 6:
                cv2.putText(frame, 'reposition', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            else:
                cv2.putText(frame, 'reposition', (10, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            # show the windows
            cv2.imshow('mask', mask)
            cv2.imshow('frame', frame)
            k = cv2.waitKey(50)
            # got ESC key? if yes - exit!
            if k == 27:
                break
            elif k == 99:  # for 'c' toggle command execution
                toggle_commands()
            elif k == 100:  # for 'd' toggle debug mode
                debug_toggle()

            # check what command to execute and run it
            com, csong, cvolume = check_command(temp)
            submit_to_tkinter(get_defects, str(temp))
            if com:
                submit_to_tkinter(get_command, com)
                submit_to_tkinter(get_song, csong)
                submit_to_tkinter(get_volume, cvolume)
        except:
            pass
