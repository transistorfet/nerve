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

    def __getattr__(self, name):
	return self.config[name]

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
    def get_class_config_info(typeinfo):
	(modulename, _, classname) = typeinfo.partition('/')
	module = ConfigObject.import_module(modulename)
	classtype = getattr(module, classname)
	return classtype.get_config_info()


class ConfigObjectTable (ConfigObject):
    def __init__(self, **config):
	ConfigObject.__init__(self, **config)
	self.set_config_data(config)

    @staticmethod
    def get_config_info():
	config_info = nerve.ConfigObject.get_config_info()
	return config_info

    def get_config_data(self):
	#config = nerve.ConfigObject.get_config_data(self)
	config = self.save_object_table(self.objects)
	return config

    def set_config_data(self, config):
	self.objects = self.make_object_table(config)

    def __getattr__(self, name):
	if name in self.objects:
	    return self.objects[name]
	return getattr(self.objects, name)

    def __iter__(self):
	return iter(self.objects)

    def __len__(self):
	return len(self.objects)

    def get_object(self, ref):
	(name, sep, remain) = ref.partition('/')
	obj = getattr(self, name)
	if remain:
	    return obj.get_object(remain)
	else:
	    return obj

    def set_object(self, ref, obj):
	if not isinstance(obj, ConfigObject):
	    raise TypeError("attempting to assign an object that is not of type ConfigObject")
	(name, sep, remain) = ref.partition('/')
	if remain:
	    self.objects[name].set_object(remain, obj)
	else:
	    self.objects[name] = obj

    @staticmethod
    def make_object_table(config):
	objects = { }
	for objname in config.keys():
	    if '__type__' not in config[objname]:
		typeinfo = "config/ConfigObjectTable"
	    else:
		typeinfo = config[objname]['__type__']
	    obj = ConfigObject.make_object(typeinfo, config[objname])
	    objects[objname] = obj
	return objects

    @staticmethod
    def save_object_table(objects):
	config = { }
	for objname in objects.keys():
	    config[objname] = objects[objname].get_config_data()
	return config


class SymbolicLink (ConfigObject):
    @staticmethod
    def get_config_info():
	config_info = nerve.ConfigObject.get_config_info()
	config_info.add_setting('link', "Link", default="")
	return config_info


