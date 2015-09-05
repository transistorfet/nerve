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

    @nerve.public
    def time(self):
        return time.time()

    @nerve.public
    def unixtime(self):
        return time.time()

    @nerve.public
    def localtime(self, format=None, secs=None):
        if not format:
            format = "%a, %d %b %Y %T %z"
        return time.strftime(format, time.localtime(secs))

    @nerve.public
    def gmt(self, format=None, secs=None):
        if not format:
            format = "%a, %d %b %Y %T %z"
        return time.strftime(format, time.gmtime(secs))

    @nerve.public
    def clocktime(self):
        return time.strftime("%H:%M:%S")

    @nerve.public
    def clockdate(self):
        return time.strftime("%Y-%m-%d")

    @nerve.public
    def timezone(self):
        return time.timezone

