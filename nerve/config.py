#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import shutil
import time
import traceback

import json


class ConfigObject (object):
    def __init__(self, **config):
	self.config = config

    @staticmethod
    def get_defaults():
	return { }

    def get_config_data(self):
	return self.config

    def get_setting(self, name, typename=None):
	if name in self.config:
	    return self.config[name]
	return None

    def set_setting(self, name, value):
	try:
	    self.config[name] = value
	except:
	    print traceback.format_exc()

    @staticmethod
    def make_object_table(config):
	objects = { }
	for objname in config.keys():
	    obj = Config.make_object(config[objname]['type'], config[objname])
	    objects[objname] = obj
	return objects

    @staticmethod
    def save_object_table(objects):
	config = { }
	for objname in objects.keys():
	    config[objname] = objects[objname].get_config_data()
	return config

    @staticmethod
    def make_object(typeinfo, config):
	(modulename, _, classname) = typeinfo.partition('/')
	# TODO should you have this? I guess the module wont be reloaded, but you don't want init called again either  It should only import once
	module = Config.import_module(modulename)
	classtype = getattr(module, classname)
	config_data = classtype.get_defaults()
	config_data.update(config)
	obj = classtype(**config_data)
	return obj

    @staticmethod
    def import_module(modulename):
	try:
	    code = 'import %s\n#%s.init()' % (modulename, modulename)
	    exec(code, globals(), globals())
	    #return eval(modulename)
	    return globals()[modulename]
	except ImportError as e:
	    #nerve.log("error loading module " + modulename + "\n\n" + traceback.format_exc())
	    raise e

    @staticmethod
    def get_object_defaults(typeinfo):
	(modulename, _, classname) = typeinfo.partition('/')
	module = Config.import_module(modulename)
	classtype = getattr(module, classname)
	return classtype.get_defaults()


class Config (ConfigObject):
    def __init__(self, configdir, root):
	ConfigObject.__init__(self)
	self.configdir = configdir.strip('/')
	self.root = root

    def set_config_data(self, config):
	self.config = config
	self.servers = self.make_object_table(config['servers'])
	self.devices = self.make_object_table(config['devices'])
	for name in self.devices.keys():
	    setattr(self.root, name, self.devices[name])

    def getdir(self):
	return self.configdir

    @staticmethod
    def get_defaults():
	defaults = ConfigObject.get_defaults()
	defaults['servers'] = { }
	defaults['devices'] = { }
	return defaults

    def get_config_data(self):
	config = ConfigObject.get_config_data(self)
	config['servers'] = self.save_object_table(self.servers)
	config['devices'] = self.save_object_table(self.devices)
	return config

    def load(self):
	config = self.get_defaults()

	filename = os.path.join(self.configdir, 'settings.json')
	if os.path.exists(filename):
	    try:
		with open(filename, 'r') as f:
		    config = json.load(f)
		    nerve.log("config loaded from " + filename)
	    except:
		nerve.log("error loading config from " + filename + "\n\n" + traceback.format_exc())
		return False
	self.set_config_data(config)
	return True

    def save(self):
	filename = os.path.join(self.configdir, 'settings.json')
	config = self.get_config_data()
	with open(filename, 'w') as f:
	    json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))

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


