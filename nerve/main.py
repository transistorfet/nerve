#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import sys
import signal
import time
import argparse
import traceback
import threading

mainloops = [ ]

class Main (object):
    def __init__(self):
	self.root = None
	self.config = None
	self.stopflag = threading.Event()

    def run(self):
	signal.signal(signal.SIGINT, self.sigint_handler)

	parser = argparse.ArgumentParser(prog='nerve', formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Nerve Control Server')
	parser.add_argument('-c', '--configdir', action='store', help='Use specified directory for configuration', default='~/.nerve/')
	self.args = parser.parse_args()

	self.root = nerve.Device()

	self.config = nerve.Config(self.args.configdir)
	if not self.config.load():
	    self.shutdown()
	if not self.config.run_init():
	    self.shutdown()

	try:
	    while not self.stopflag.wait(0.5):
		pass
	    nerve.log("exiting main loop")
	except:
	    nerve.log(traceback.format_exc())

	self.shutdown()

    def sigint_handler(self, signal, frame):
	#print "received sigint"
	self.stopflag.set()

    def shutdown(self):
	nerve.log("shutting down all threads")
	nerve.Task.stop_all()
	nerve.Task.join_all()
	sys.exit(0)

def log(text):
    print time.strftime("%Y-%m-%d %H:%M") + " " + text

def loop():
    global mainloops

    main = Main()
    mainloops.insert(0, main)
    main.run()

def quit():
    global mainloops
    main = mainloops.pop(0)
    self.stopflag.set()


def get_config(name):
    global mainloops
    return mainloops[0].config.get(name)

def set_config(name, value):
    global mainloops
    return mainloops[0].config.set(name, value)

def configdir():
    global mainloops
    return mainloops[0].config.getdir()

def add_portal(portal, *args):
    global mainloops
    return mainloops[0].config.create_object('portals', portal, *args)

def add_device(name, dev, *args):
    global mainloops
    if not isinstance(dev, nerve.Device):
	dev = mainloops[0].config.create_object('devices', dev, *args)
    return mainloops[0].root.add(name, dev)

def get_device(name):
    global mainloops
    return mainloops[0].root.get(name)

def query(line, addr=None, server=None):
    global mainloops
    mainloops[0].root.query(line, addr, server)

def dispatch(msg):
    global mainloops
    mainloops[0].root.dispatch(msg)

