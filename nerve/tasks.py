#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import threading

class Task (threading.Thread):
    threads = []

    def __init__(self, name=None, target=None):
        threading.Thread.__init__(self, None, target, name)
        Task.threads.insert(0, self)
        self.stopflag = threading.Event()

    def finish(self):
        Task.threads.remove(self)

    def start(self):
        nerve.log("starting thread <%s>" % (str(self.name),))
        threading.Thread.start(self)

    def stop(self):
        nerve.log("stopping thread <%s>" % (str(self.name),))
        self.stopflag.set()

    @staticmethod
    def stop_all():
        for t in Task.threads:
            t.stop()

    @staticmethod
    def join_all():
        for t in Task.threads:
            if t.daemon is False:
                t.join() 

