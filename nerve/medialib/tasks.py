#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import traceback


class MediaLibUpdater (object):
    def __init__(self, task):
        raise NotImplementedError

    def set_config(self, paths):
        raise NotImplementedError

    def check_update(self):
        raise NotImplementedError

    def run_update(self):
        raise NotImplementedError


class MediaLibUpdaterTask (nerve.Task):
    def __init__(self):
        super().__init__("MediaLibUpdaterTask")
        self.updaters = { }

    def add(self, name, updater):
        self.updaters[name] = updater

    def run(self):
        while True:
            try:
                for name in self.updaters.keys():
                    self.updaters[name].check_update()
            except:
                nerve.log(traceback.format_exc())

            if self.stopflag.wait(60):
                break


