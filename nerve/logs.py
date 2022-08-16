#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import queue
import nerve

thread = None
thread_queue = queue.Queue()
thread_running = False

stdin = sys.stdin
stdout = sys.stderr

logbuffer = [ ]
logbuffermax = 2000

logto = stdout
logtofile = False

colours = { }
colours_reset = ''

def init_colour():
    global thread, colours, colours_reset

    import colorama

    colorama.init()

    colours_reset = colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL
    colours = {
        'info': '',
        'error': colorama.Style.BRIGHT + colorama.Fore.RED,
        'warning': colorama.Style.BRIGHT + colorama.Fore.YELLOW,
        'success': colorama.Fore.GREEN,
        'query': colorama.Style.BRIGHT + colorama.Fore.BLUE,
        'debug': colorama.Style.BRIGHT + colorama.Fore.BLACK,
        'event': colorama.Style.BRIGHT + colorama.Fore.CYAN,
        'notify': colorama.Style.BRIGHT + colorama.Fore.MAGENTA
    }

    thread = nerve.Thread('SerialThread', run_logger)
    thread.start()

def redirect(dest):
    global logto
    logto = dest

def buffer():
    return list(logbuffer)

def log_to_file(enable):
    global logtofile
    nerve.files.createdir('logs')
    logtofile = True if enable is True else False

def log(text, logtype='info'):
    global thread_queue, thread_running

    # Log messages directly until the logging thread has started
    if not thread_running:
        log_direct(text, logtype)
    else:
        thread_queue.put((logtype, text))

def log_direct(text, logtype='info'):
    global logbuffer

    #output = "%s %s\n" % (time.strftime("%Y-%m-%d %H:%M"), text)
    output = "%s [%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M"), logtype, text)

    logbuffer.append(output)
    if len(logbuffer) > logbuffermax:
        logbuffer = logbuffer[logbuffermax - len(logbuffer):]

    if logtofile:
        with open(nerve.files.path('logs/{0}.txt'.format(time.strftime("%Y-%m-%d"))), 'a') as f:
            f.write(output)

    if logto:
        colour = colours[logtype] if logtype in colours else ''
        print(colour + output + colours_reset, end='', file=logto)

def run_logger():
    global thread, thread_queue, thread_running

    thread_running = True
    while not thread.stopflag.is_set():
        try:
            (logtype, text) = thread_queue.get()
            log_direct(text, logtype)
        except queue.Empty as e:
            pass

