#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time


stdin = sys.stdin
stdout = sys.stdout

logbuffer = [ ]
logbuffermax = 2000

logto = stdout

def redirect(dest):
    global logto
    logto = dest

def buffer():
    return list(logbuffer)

def log(logtype, text=None):
    global logbuffer

    if text is None:
        text = logtype
        logtype = 'info'
    #output = "%s [%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M"), logtype, text)
    output = "%s %s\n" % (time.strftime("%Y-%m-%d %H:%M"), text)

    logbuffer.append(output)
    if len(logbuffer) > logbuffermax:
        logbuffer = logbuffer[logbuffermax - len(logbuffer):]

    if logto:
        logto.write(output)


