#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import threading


class Task (threading.Thread):
    delay = True
    threads = []
    quit = False

    def __init__(self, name=None, target=None):
        threading.Thread.__init__(self, None, target, name)
        Task.threads.insert(0, self)
        self.stopflag = threading.Event()

    def start(self):
        if Task.delay:
            return
        nerve.log("starting thread <%s>" % (str(self.name),))
        threading.Thread.start(self)

    def stop(self):
        nerve.log("stopping thread <%s>" % (str(self.name),))
        self.stopflag.set()

    def delete(self):
        Task.threads.remove(self)

    @classmethod
    def start_all(cls):
        cls.delay = False
        for t in cls.threads:
            t.start()

    @classmethod
    def stop_all(cls):
        if cls.delay:
            return
        cls.quit = True
        for t in cls.threads:
            t.stop()

    @classmethod
    def join_all(cls):
        if cls.delay:
            return
        for t in cls.threads:
            if t.daemon is False:
                t.join() 

