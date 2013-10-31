
import win32api
import win32con
import os

import nerve

class Win32Sys (nerve.Device):
    def wakeup(self, msg):
	win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
	win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

    def sleep(self, msg):
	os.system("C:\\Windows\\System32\\scrnsave.scr /s");

 
