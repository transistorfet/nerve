#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import os

class SystemDevice (nerve.Device):
    def cputemp(self):
	with open("/sys/class/thermal/thermal_zone2/temp", 'r') as f:
	    contents = f.read()
	return float(contents) / 1000.0

    def sleep(self):
	os.system("xscreensaver-command -activate")

    def wakeup(self):
	os.system("xscreensaver-command -deactivate") 

