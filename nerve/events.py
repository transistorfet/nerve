#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import queue
import threading
import traceback


class Event (nerve.ObjectNode):
    events = [ ]

    def __init__(self, **config):
        super().__init__(**config)
        Event.events.append(self)

        repeat = self.get_setting('repeat')
        if repeat and repeat > 0.0:
            self.repeat_in(repeat)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('repeat', "Repeat Time", default=0.0)
        config_info.add_setting('trigger', "Trigger", default='')
        return config_info

    def __call__(self, *args, **kwargs):
        trigger = self.get_setting('trigger')
        if trigger and (len(args) <= 0 or str(args[0]) != self.trigger):
            return False

        root = self.get_root()
        if not root:
            return False
        root.eventpool.schedule_now(self, *args, **kwargs)
        return True

    def __lt__(self, other):
        return False

    def do_event(self, *args, **kwargs):
        self.execute(*args, **kwargs)
        repeat = self.get_setting('repeat')
        if repeat and repeat > 0.0:
            self.repeat_in(repeat)

    def repeat_in(self, timeout, *args, **kwargs):
        root = self.get_root()
        if not root:
            return False
        self.eventpool.schedule(timeout, self, *args, **kwargs)

    def execute(self, *args, **kwargs):
        raise NotImplementedError


class PyCodeEvent (Event):
    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('code', "Python Code", default='', datatype='textarea')
        return config_info

    def execute(self, *args, **kwargs):
        code = self.get_setting('code')
        exec(code)


class EventThreadPool (nerve.Task):
    def __init__(self):
        super().__init__("EventSchedulerTask")
        self.queue = queue.PriorityQueue()

    def schedule_now(self, event, *args, **kwargs):
        self.schedule(0.0, event, *args, **kwargs)

    def schedule(self, timeout, event, *args, **kwargs):
        for (_, q_event, _, _) in self.queue.queue:
            if event == q_event:
                nerve.log("event already scheduled")
                return
        self.queue.put((time.time() + timeout, event, args, kwargs))

    def stop(self):
        super().stop()
        #self.queue.join()

    def run(self):
        while True:
            if self.stopflag.is_set():
                break
            try:
                (run_at, event, args, kwargs) = self.queue.get(timeout=0.25)
                timeout = run_at - time.time()
                if timeout > 0:
                    if self.stopflag.wait(timeout):
                        break
                try:
                    event.do_event(*args, **kwargs)
                    #self.queue.task_done()
                except:
                    nerve.log(traceback.format_exc())
            except queue.Empty:
                pass


