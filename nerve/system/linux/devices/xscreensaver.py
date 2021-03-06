#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os

class ScreenSaverDevice (nerve.Device):
    def run(self):
        os.system("xdg-open /etc/xdg/autostart/xscreensaver.desktop")

    def exit(self):
        os.system("xscreensaver-command -exit")

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

    def pause(self, duration=60):
        self.exit()


