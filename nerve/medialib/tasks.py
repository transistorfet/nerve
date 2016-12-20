#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import threading
import traceback


updater_task = None

def start_updater(updaters):
    global updater_task
    if updater_task:
        return
    updater_task = MediaLibUpdaterTask()
    #updater_task.add('files', MediaFilesUpdater())
    #updater_task.add('youtube', YoutubePlaylistUpdater())
    for updater in updaters:
        names = updater.split('/')
        classtype = nerve.Module.get_class(updater)
        updater_task.add(names[-2] if len(names) >= 2 else '', classtype())
    updater_task.start()

def run_updater():
    updater_task.run_updater()


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
            for name in self.updaters.keys():
                try:
                    self.updaters[name].check_update()
                except:
                    nerve.log(traceback.format_exc(), logtype='error')

            #nerve.query('/devices/notify/send', 'medialib update complete')

            if self.stopflag.is_set():
                break

            if self.interrupt.wait(60):
                self.interrupt.clear()

    def stop(self):
        super().stop()
        for name in self.updaters.keys():
            self.updaters[name].stop()
        self.interrupt.set()

    def run_updater(self):
        for name in self.updaters.keys():
            self.updaters[name].reset_check()
        self.interrupt.set()    


