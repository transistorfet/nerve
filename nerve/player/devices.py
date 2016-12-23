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
        #self.driver = None

        #backend = self.get_setting('backend')
        #try:
        #    self.driver = nerve.ObjectNode.make_object(backend['__type__'], backend)
        #except:
        #    nerve.log("failed to initialize player backend: " + backend, logtype='error')
        #    nerve.log(traceback.format_exc(), logtype='error')

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        #config_info.add_setting('backend', "Player Backend", datatype='object', default={ '__type__': 'player/vlc/VLCHTTP' })
        #for option in os.listdir(nerve.files.find_source('nerve/player')):
        #    if option != '__pycache__' and os.path.isdir('nerve/player/' + option):
        #        config_info.add_option('backend', option, 'player/' + option)
        config_info.add_setting('backend', "Player Backend", default='vlc')
        return config_info

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            pass
        #return getattr(self.driver, name)
        backend = self.get_child(self.get_setting('backend'))
        if not backend:
            raise Exception("invalid player backend selected")
        return getattr(backend, name)

    def select_backend(self, name):
        if self.get_child(name):
            self.set_setting('backend', name)

