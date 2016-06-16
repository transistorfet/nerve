#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import os.path

class SysFSDevice (nerve.Device):
    def query(self, querystring, *args, **kwargs):
        segments = querystring.split('/')

        if segments[0] == 'thermal' and len(segments) == 2:
            path = '/sys/class/thermal/thermal_zone{0}/temp'.format(segments[1])
            if os.path.exists(path):
                with open(path, 'r') as f:
                    contents = f.read()
                return float(contents) / 1000.0

        raise Exception("invalid sysfs reference: " + querystring)

