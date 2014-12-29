#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve


class SysFiles (nerve.Device):
    def cputemp(self):
	with open("/sys/class/thermal/thermal_zone2/temp", 'r') as f:
	    contents = f.read()
	return float(contents) / 1000

 
