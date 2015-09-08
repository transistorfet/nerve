#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import traceback
import subprocess


class ProjectMDevice (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.process = None

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        return config_info

    @nerve.public
    def start(self):
        if not self.process:
            self.process = subprocess.Popen([ 'projectM-pulseaudio' ], stdin=None, stdout=None, stderr=None, close_fds=True, shell=False)
        else:
            self.raise_window()

    @nerve.public
    def stop(self):
        if self.process:
            self.process.kill()
            self.process = None

    @nerve.public
    def raise_window(self):
        os.system('xdotool search --class "projectM" windowraise')

    @nerve.public
    def fullscreen(self):
        os.system('xdotool search --class "projectM" key f windowraise')

    @nerve.public
    def minimize(self):
        os.system('xdotool search --class "projectM" key f minimize')


