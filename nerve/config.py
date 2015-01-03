#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import shutil
import time
import traceback

import json

class ConfigInfo (object):
    def __init__(self):
	self.settings = [ ]

    def add_setting(self, name, propername, default=None):
	for i in xrange(len(self.settings)):
	    if self.settings[i][0] == name:
		del self.settings[i]
		break
	self.settings.append([ name, propername, default ])

    def get_defaults(self):
	defaults = { }
	for setting in self.settings:
	    defaults[setting[0]] = setting[2]
	return defaults

    def get_proper_names(self):
	return [ [ setting[0], setting[1] ] for setting in self.settings ]


class ConfigObject (object):
    def __init__(self, **config):
	self.config = config

    @staticmethod
    def get_config_info():
	return ConfigInfo()

    def get_config_data(self):
	return self.config

    def set_config_data(self, config):
	self.config = config

    def get_setting(self, name, typename=None):
	if name in self.config:
	    return self.config[name]
	return None

    def set_setting(self, name, value):
	try:
	    self.config[name] = value
	except:
	    print traceback.format_exc()

    def load_config(self, filename):
	config = self.get_config_info().get_defaults()

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

    def save_config(self, filename):
	config = self.get_config_data()
	with open(filename, 'w') as f:
	    json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))

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
    def make_object(typeinfo, config):
	(modulename, _, classname) = typeinfo.partition('/')
	# TODO should you have this? I guess the module wont be reloaded, but you don't want init called again either  It should only import once
	module = ConfigObject.import_module(modulename)
	classtype = getattr(module, classname)
	config_data = classtype.get_config_info().get_defaults()
	config_data.update(config)
	obj = classtype(**config_data)
	return obj

    @staticmethod
    def make_object_table(config):
	objects = { }
	for objname in config.keys():
	    obj = ConfigObject.make_object(config[objname]['type'], config[objname])
	    objects[objname] = obj
	return objects

    @staticmethod
    def save_object_table(objects):
	config = { }
	for objname in objects.keys():
	    config[objname] = objects[objname].get_config_data()
	return config

    @staticmethod
    def get_class_config_info(typeinfo):
	(modulename, _, classname) = typeinfo.partition('/')
	module = ConfigObject.import_module(modulename)
	classtype = getattr(module, classname)
	return classtype.get_config_info()



