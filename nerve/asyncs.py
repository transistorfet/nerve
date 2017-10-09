#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import queue
import threading
import traceback


_asynctaskpool = None

def init():
    global _asynctaskpool
    _asynctaskpool = AsyncTaskThreadPool()
    _asynctaskpool.start()


class AsyncTask (nerve.ObjectNode):
    #asynctasks = [ ]

    def __init__(self, **config):
        super().__init__(**config)
        #AsyncTask.asynctasks.append(self)

        #repeat = self.get_setting('repeat')
        #if repeat and repeat > 0.0:
        #    self.repeat_in(repeat)

        if self.get_setting('autorun'):
            self()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('autorun', "Run on Startup", default=False)
        config_info.add_setting('repeat', "Repeat Time", default=0.0)
        return config_info

    def __call__(self, *args, **kwargs):
        _asynctaskpool.schedule_now(self, *args, **kwargs)
        return True

    def __lt__(self, other):
        return False

    def do_asynctask(self, *args, **kwargs):
        self.execute(*args, **kwargs)
        repeat = self.get_setting('repeat')
        if repeat and repeat > 0.0:
            self.repeat_in(repeat)

    def repeat_in(self, timeout, *args, **kwargs):
        _asynctaskpool.schedule(timeout, self, *args, **kwargs)

    def execute(self, *args, **kwargs):
        raise NotImplementedError

    def kill(self):
        _asynctaskpool.kill(self)


class PyCodeAsyncTask (AsyncTask, nerve.PyCodeQuery):
    def execute(self, *args, **kwargs):
        #nerve.PyCodeQuery.execute(self, *args, **kwargs)
        self._compiledfunc(self, *args, **kwargs)


class AsyncTaskThreadPool (nerve.Thread):
    _singleton = None

    def __new__(cls):
        if not cls._singleton:
            cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(self):
        super().__init__("AsyncTaskSchedulerTask")
        self.queue = queue.PriorityQueue()
        self.check = threading.Condition()

    def schedule_now(self, asynctask, *args, **kwargs):
        self.schedule(0.0, asynctask, *args, **kwargs)

    def schedule(self, timeout, asynctask, *args, **kwargs):
        for (_, q_asynctask, _, _) in self.queue.queue:
            if asynctask == q_asynctask:
                nerve.log("asynctask already scheduled")
                # TODO maybe we should only reschedule the asynctask if the new time is less than the old time
                return
        self.queue.put((time.time() + timeout, asynctask, args, kwargs))
        with self.check:
            self.check.notify()

    def kill(self, asynctask):
        with self.queue.mutex:
            i = 0
            while i < len(self.queue.queue):
                if self.queue.queue[i][1] == asynctask:
                    self.queue.queue.pop(i)
                else:
                    i += 1

    def stop(self):
        super().stop()
        with self.check:
            self.check.notify()
        #self.queue.join()

    def run(self):
        while True:
            if self.stopflag.is_set():
                break
            try:
                (run_at, asynctask, args, kwargs) = self.queue.get(timeout=0.25)
                timeout = run_at - time.time()

                if timeout <= 0:
                    try:
                        asynctask.do_asynctask(*args, **kwargs)
                        #self.queue.task_done()
                    except:
                        nerve.log(traceback.format_exc(), logtype='error')
                else:
                    self.queue.put((run_at, asynctask, args, kwargs))

            except queue.Empty:
                timeout = 60
                pass

            with self.check:
                self.check.wait(timeout)



