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
    def toggle_fullscreen(self):
        os.system('xdotool search --class "projectM" key f windowraise')

    @nerve.public
    def minimize(self):
        os.system('xdotool search --class "projectM" key f minimize')

    @nerve.public
    def next(self):
        os.system('xdotool search --class "projectM" key n')

    @nerve.public
    def previous(self):
        os.system('xdotool search --class "projectM" key p')

    @nerve.public
    def random(self):
        os.system('xdotool search --class "projectM" key r')

    @nerve.public
    def toggle_lock(self):
        os.system('xdotool search --class "projectM" key l')

    @nerve.public
    def toggle_name(self):
        os.system('xdotool search --class "projectM" key F3')

    @nerve.public
    def toggle_info(self):
        os.system('xdotool search --class "projectM" key F4')

    @nerve.public
    def toggle_fps(self):
        os.system('xdotool search --class "projectM" key F5')

