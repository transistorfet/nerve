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

mainloops = [ ]
stdout = sys.stdout


class Main (nerve.ConfigObject):
    def __init__(self):
	nerve.ConfigObject.__init__(self)
	self.root = None
	self.stopflag = threading.Event()

	parser = argparse.ArgumentParser(prog='nerve', formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Nerve Control Server')
	parser.add_argument('-c', '--configdir', action='store', help='Use specified directory for configuration', default='~/.nerve/')
	self.args = parser.parse_args()

	self.configdir = self.args.configdir.strip('/')

    @staticmethod
    def get_config_info():
	config_info = nerve.ConfigObject.get_config_info()
	config_info.add_setting('servers', "Servers", default=dict())
	config_info.add_setting('devices', "Devices", default=dict())
	return config_info

    def get_config_data(self):
	config = nerve.ConfigObject.get_config_data(self)
	config['servers'] = self.save_object_table(self.servers)
	config['devices'] = self.save_object_table(self.devices)
	return config

    def set_config_data(self, config):
	nerve.ConfigObject.set_config_data(self, config)
	self.servers = self.make_object_table(config['servers'])
	self.devices = self.make_object_table(config['devices'])
	for name in self.devices.keys():
	    setattr(self.root, name, self.devices[name])

    def getdir(self):
	return self.configdir

    def start(self):
	signal.signal(signal.SIGINT, self.signal_handler)

	self.root = nerve.Device()

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

    def add_server(self, name, server, **config):
	if not isinstance(server, nerve.Server):
	    server = self.make_object(server, config)
	if not server:
	    nerve.log("error creating server object " + name + " of type " + typeinfo)
	    return
	self.servers[name] = server
	return server

    def get_server(self, name):
	if name in self.servers:
	    return self.servers[name]
	return None

    def add_device(self, name, dev, **config):
	if not isinstance(dev, nerve.Device):
	    dev = self.make_object(dev, config)
	if not dev:
	    nerve.log("error creating server object " + name + " of type " + typeinfo)
	    return
	self.devices[name] = dev
	setattr(self.root, name, dev)
	return dev

    def get_device(self, name):
	(name, sep, remain) = name.partition('.')
	if remain:
	    # TODO support dotnames
	    return "POOP"
	if name in self.devices:
	    return self.devices[name]
	return None

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

def save_config():
    global mainloops
    return mainloops[0].save_config()

def configdir():
    global mainloops
    return mainloops[0].getdir()

def add_server(name, servername, **config):
    global mainloops
    return mainloops[0].add_server(name, servername, **config)

def get_server(name):
    global mainloops
    return mainloops[0].get_server(name)
    return None

def add_device(name, dev, **config):
    global mainloops
    dev = mainloops[0].add_device(name, dev, **config)
    return dev

def get_device(name):
    global mainloops
    return mainloops[0].get_device(name)

def query(ref, *args, **kwargs):
    # TODO should this be ref or tag or point or what
    global mainloops
    return mainloops[0].root.query(ref, *args, **kwargs)

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

