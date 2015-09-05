#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import time
import socket
import platform
import traceback
import subprocess


class PlayerDevice (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.driver = None

        backend = self.get_setting('backend')
        try:
            self.driver = nerve.Module.make_object(backend, config)
        except:
            nerve.log("failed to initialize player backend: " + backend)
            nerve.log(traceback.format_exc())

        self.playlist = []

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('backend', "Player Backend", default='player/vlc/VLCHTTP')
        for option in os.listdir('nerve/player'):
            if option != '__pycache__' and os.path.isdir('nerve/player/' + option):
                config_info.add_option('backend', option, 'player/' + option)
        return config_info

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            pass
        return getattr(self.driver, name)


