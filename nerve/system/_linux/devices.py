#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os

class SystemDevice (nerve.Device):
    def cputemp(self):
        with open("/sys/class/thermal/thermal_zone2/temp", 'r') as f:
            contents = f.read()
        return float(contents) / 1000.0

    def systemp1(self):
        with open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
            contents = f.read()
        return float(contents) / 1000.0

    def systemp2(self):
        with open("/sys/class/thermal/thermal_zone1/temp", 'r') as f:
            contents = f.read()
        return float(contents) / 1000.0

    def sleep(self):
        os.system("xscreensaver-command -activate")

    def wakeup(self):
        os.system("xscreensaver-command -deactivate")

    def cycle_screensaver(self):
        os.system("xscreensaver-command -cycle")

    def next_screensaver(self):
        os.system("xscreensaver-command -next")

    def previous_screensaver(self):
        os.system("xscreensaver-command -prev")

    def mouse_click(self):
        os.system("xdotool getactivewindow mousemove -window %1 200 200 click 1")

    def xdotool(self, commands):
        os.system("xdotool " + commands)

