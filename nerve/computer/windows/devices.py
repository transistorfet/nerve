#!/usr/bin/python3
# -*- coding: utf-8 -*-

import win32api
import win32con
import os

import nerve

class SystemDevice (nerve.Device):
    def wakeup(self):
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

    def sleep(self):
        os.system("C:\\Windows\\System32\\scrnsave.scr /s");

 
