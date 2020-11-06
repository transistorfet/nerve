#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import os.path

class SystemDevice (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        #if os.path.isdir('/sys'):
        #    # TODO add sysfs device somehow... if you add it to children, you have to check for it first.
        #    pass

    def mouse_click(self):
        os.system("xdotool getactivewindow mousemove -window %1 200 200 click 1")

    def xdotool(self, commands):
        os.system("xdotool " + commands)

    def browser(self, url):
        os.system("sensible-browser " + url)


