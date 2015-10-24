#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time

import colorama

colorama.init()

stdin = sys.stdin
stdout = sys.stdout

logbuffer = [ ]
logbuffermax = 2000

logto = stdout

colours = {
    'info': '',
    'error': colorama.Style.BRIGHT + colorama.Fore.RED,
    'warning': colorama.Style.BRIGHT + colorama.Fore.YELLOW,
    'success': colorama.Fore.GREEN,
    'query': colorama.Style.BRIGHT + colorama.Fore.BLUE,
    'debug': colorama.Style.BRIGHT + colorama.Fore.BLACK
}

colour_reset = colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL

def redirect(dest):
    global logto
    logto = dest

def buffer():
    return list(logbuffer)

def log(text, logtype='info'):
    global logbuffer

    output = "%s [%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M"), logtype, text)
    #output = "%s %s\n" % (time.strftime("%Y-%m-%d %H:%M"), text)

    logbuffer.append(output)
    if len(logbuffer) > logbuffermax:
        logbuffer = logbuffer[logbuffermax - len(logbuffer):]

    if logto:
        colour = colours[logtype] if logtype in colours else ''
        logto.write(colour + output + colour_reset)


