#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import time
import signal
import os.path
import argparse
import traceback
import threading

import json
import urlparse
import requests

mainloops = [ ]
stdout = sys.stdout


class Main (nerve.ConfigObjectTable):
    def __init__(self):
	nerve.ConfigObjectTable.__init__(self)
	self.stopflag = threading.Event()

	parser = argparse.ArgumentParser(prog='nerve', formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Nerve Control Server')
	parser.add_argument('-c', '--configdir', action='store', help='Use specified directory for configuration', default='~/.nerve/')
	self.args = parser.parse_args()

	self.configdir = self.args.configdir.strip('/')

    @staticmethod
    def get_config_info():
	config_info = nerve.ConfigObjectTable.get_config_info()
	config_info.add_setting('servers', "Servers", default=nerve.ConfigObjectTable())
	config_info.add_setting('devices', "Devices", default=nerve.ConfigObjectTable())
	return config_info

    def getdir(self):
	return self.configdir

    def start(self):
	signal.signal(signal.SIGINT, self.signal_handler)

	try:
	    if not self.load_config(os.path.join(self.configdir, 'settings.json')):
		self.shutdown()
	    if not self.run_init():
		self.shutdown()

	    #print dir(nerve)
	    while not self.stopflag.wait(0.5):
		pass
	    nerve.log("exiting main loop")
	except:
	    nerve.log(traceback.format_exc())

	self.shutdown()

    def signal_handler(self, signal, frame):
	self.stopflag.set()

    def shutdown(self):
	nerve.log("shutting down all threads")
	nerve.Task.stop_all()
	nerve.Task.join_all()
	os.system('stty sane')
	sys.exit(0)

    def run_init(self):
	filename = os.path.join(self.configdir, 'init.py')
	if not os.path.exists(filename):
	    return True

	nerve.log("running init script located at " + filename)
	try:
	    with open(filename, 'r') as f:
		code = f.read()
	    self.init = { 'nerve' : nerve }
	    exec(code, self.init)
	    nerve.log(filename + " has completed sucessfully")
	    return True
	except:
	    nerve.log("error running init from " + filename + "\n\n" + traceback.format_exc())
	    return False

    def get_config_file(self, filename):
	filename = os.path.join(self.configdir, filename)
	(path, _, _) = filename.rpartition('/')
	if not os.path.isdir(path):
	    os.makedirs(path)
	if not os.path.isfile(filename):
	    with open(filename, 'w'):
		pass
	with open(filename, 'r') as f:
	    contents = f.read()
	return contents

    def write_config_file(self, filename, contents):
	filename = os.path.join(self.configdir, filename)
	(path, _, _) = filename.rpartition('/')
	if not os.path.isdir(path):
	    os.makedirs(path)
	with open(filename, 'w') as f:
	    f.write(contents)


def log(text):
    global stdout
    stdout.write(time.strftime("%Y-%m-%d %H:%M") + " " + text + "\n")

def loop():
    global mainloops

    main = Main()
    mainloops.insert(0, main)
    main.start()

def quit():
    global mainloops
    main = mainloops.pop(0)
    self.stopflag.set()

def main():
    global mainloops
    return mainloops[0]

def get_config_info():
    global mainloops
    return mainloops[0].get_config_info()

def get_config_data():
    global mainloops
    return mainloops[0].get_config_data()

def configdir():
    global mainloops
    return mainloops[0].getdir()

def save_config():
    global mainloops
    return mainloops[0].save_config(os.path.join(nerve.configdir(), 'settings.json'))

def set_object(name, obj, **config):
    global mainloops
    if type(obj) == str:
	obj = nerve.ConfigObject.make_object(obj, config)
    if not obj:
	nerve.log("error creating object " + name)
	return None
    return mainloops[0].set_object(name, obj)

def get_object(name):
    global mainloops
    return mainloops[0].get_object(name)

def add_server(name, obj, **config):
    return nerve.set_object('servers/' + name, obj, **config)

def get_server(name):
    global mainloops
    return mainloops[0].server.get_object(name)

def add_device(name, obj, **config):
    return nerve.set_object('devices/' + name, obj, **config)

def get_device(name):
    global mainloops
    return mainloops[0].devices.get_object(name)

def query(urlstring, *args, **kwargs):
    global mainloops
    nerve.log("executing query: " + urlstring + " " + ' '.join(args) + " " + repr(kwargs))
    url = urlparse.urlparse(urlstring)
    if url.netloc:
	if url.scheme == 'http':
	    nerve.log("remote query to " + urlstring)
	    r = requests.get(urlstring)
	    if r.status_code == 200:
		return json.loads(r.text)
	    else:
		return "request to " + urlstring + " failed. " + str(r.status_code) + " returned"
    else:
	(objname, sep, funcname) = url.path.replace('.', '/').lstrip('/').rpartition('/')
	obj = mainloops[0].devices.get_object(objname)
	if funcname:
	    func = getattr(obj, funcname)
	    return func(*args, **kwargs)
	else:
	    return obj

def query_string(text):
    # TODO parse quotes
    args = text.split()
    ref = args.pop(0)
    return query(ref, *args)


def get_config_file(filename):
    global mainloops
    return mainloops[0].get_config_file(filename)

def write_config_file(filename, contents):
    global mainloops
    return mainloops[0].write_config_file(filename, contents)

