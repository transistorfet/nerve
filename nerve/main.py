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
stdout = sys.stdout

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

	#self.root = nerve.Device()

	try:
	    self.config = nerve.Config(self.args.configdir, nerve.Device())
	    if not self.config.load() or not self.config.run_init():
		self.shutdown()

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
    global stdout
    stdout.write(time.strftime("%Y-%m-%d %H:%M") + " " + text + "\n")

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
    #return mainloops[0].config.get(name)
    return ""

def set_config(name, value):
    global mainloops
    #return mainloops[0].config.set(name, value)

def get_config_data():
    global mainloops
    return mainloops[0].config.get_config_data()
    
def save_config():
    global mainloops
    return mainloops[0].config.save()

def configdir():
    global mainloops
    return mainloops[0].config.getdir()

def add_server(name, servername, **config):
    global mainloops
    return mainloops[0].config.add_server(name, servername, **config)

def get_server(name):
    global mainloops
    return mainloops[0].config.get_server(name)
    return None

def add_device(name, dev, **config):
    global mainloops
    dev = mainloops[0].config.add_device(name, dev, **config)
    #setattr(mainloops[0].root, name, dev)
    return dev

def get_device(name):
    global mainloops
    return mainloops[0].config.get_device(name)

def query(ref, *args, **kwargs):
    # TODO should this be ref or tag or point or what
    global mainloops
    return mainloops[0].config.root.query(ref, *args, **kwargs)

def query_string(text):
    # TODO parse quotes
    args = text.split()
    ref = args.pop(0)
    return query(ref, *args)

