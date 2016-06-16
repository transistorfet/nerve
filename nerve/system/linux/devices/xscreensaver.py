#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os

class ScreenSaverDevice (nerve.Device):
    def activate(self):
        os.system("xscreensaver-command -activate")

    def deactivate(self):
        os.system("xscreensaver-command -deactivate")

    def lock(self):
        os.system("xscreensaver-command -lock")

    def cycle(self):
        os.system("xscreensaver-command -cycle")

    def next(self):
        os.system("xscreensaver-command -next")

    def previous(self):
        os.system("xscreensaver-command -prev")

    def restart(self):
        os.system("xscreensaver-command -restart")

    def demo(self):
        os.system("xscreensaver-command -demo")

