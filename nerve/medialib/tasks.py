#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import threading
import traceback


class MediaLibUpdater (object):
    def __init__(self):
        self.stopflag = threading.Event()

    def stop(self):
        self.stopflag.set()

    def set_config(self, paths):
        raise NotImplementedError

    def reset_check(self):
        raise NotImplementedError

    def check_update(self):
        raise NotImplementedError

    def run_update(self):
        raise NotImplementedError


class MediaLibUpdaterTask (nerve.Task):
    def __init__(self):
        super().__init__("MediaLibUpdaterTask")
        self.updaters = { }
        self.interrupt = threading.Event()

    def add(self, name, updater):
        self.updaters[name] = updater

    def run(self):
        while True:
            try:
                for name in self.updaters.keys():
                    self.updaters[name].check_update()
            except:
                nerve.log(traceback.format_exc(), logtype='error')

            if self.stopflag.is_set():
                break

            self.interrupt.wait(60)

    def stop(self):
        super().stop()
        for name in self.updaters.keys():
            self.updaters[name].stop()
        self.interrupt.set()

    def run_updater(self):
        for name in self.updaters.keys():
            self.updaters[name].reset_check()
        self.interrupt.set()    


