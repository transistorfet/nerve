#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time


class RealtimeDevice (nerve.Device):
    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        return config_info

    def __call__(self):
        return time.localtime()

    @nerve.querymethod
    def time(self):
        return time.time()

    @nerve.querymethod
    def unixtime(self):
        return time.time()

    @nerve.querymethod
    def localtime(self, format=None, secs=None):
        if not format:
            format = "%a, %d %b %Y %T %z"
        return time.strftime(format, time.localtime(secs))

    @nerve.querymethod
    def gmt(self, format=None, secs=None):
        if not format:
            format = "%a, %d %b %Y %T %z"
        return time.strftime(format, time.gmtime(secs))

    @nerve.querymethod
    def clocktime(self):
        return time.strftime("%H:%M:%S")

    @nerve.querymethod
    def clockdate(self):
        return time.strftime("%Y-%m-%d")

    @nerve.querymethod
    def timezone(self):
        return time.timezone

