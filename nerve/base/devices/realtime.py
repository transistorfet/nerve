#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time


class RealtimeDevice (nerve.Device):
    @staticmethod
    def get_config_info():
        config_info = nerve.Device.get_config_info()
        return config_info

    def __call__(self):
        return time.localtime()

    def time(self):
        return time.time()

    def unixtime(self):
        return time.time()

    def localtime(self, format=None, secs=None):
        if not format:
            format = "%a, %d %b %Y %T %z"
        return time.strftime(format, time.localtime(secs))

    def gmt(self, format=None, secs=None):
        if not format:
            format = "%a, %d %b %Y %T %z"
        return time.strftime(format, time.gmtime(secs))

    def clocktime(self):
        return time.strftime("%H:%M:%S")

    def clockdate(self):
        return time.strftime("%Y-%m-%d")

    def timezone(self):
        return time.timezone

