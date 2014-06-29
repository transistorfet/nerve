#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import shutil
import time
import traceback

import json


class Config (object):
    settings_file = 'settings.json'
    init_file = 'init.py'

    def __init__(self, configdir=None):
	self.path = [ 'config/default', 'nerve' ]
	if configdir is not None:
	    sys.path.insert(0, configdir)
	    self.path.insert(0, configdir.strip('/'))
	self.data = [ { } ]	# a blank dict, in case set() is called before load()
	self.init = None

    def getdir(self):
	return self.path[0]

    def get(self, name, type=None):
	# TODO check type
	for data in self.data:
	    if name in data:
		return data[name]
	return None

    def set(self, name, value):
	try:
	    self.data[0][name] = value
	except:
	    print traceback.format_exc()

    def load(self):
	files = self.find_file(Config.settings_file, all=True)
	if len(files) <= 0:
	    #shutil.copyfile('share/settings.py', self.path[0] + '/settings.py')
	    return True

	self.data = [ ]
	for filename in reversed(files):
	    try:
		with open(filename, 'r') as f:
		    self.data.append(json.load(f))
		    nerve.log("config loaded from " + filename)
	    except:
		nerve.log("error loading config from " + filename + "\n\n" + traceback.format_exc())
		return False
	return True

    def save(self):
	filename = self.path[0] + '/' + Config.settings_file
	with open(filename, 'w') as f:
	    json.dump(self.data[0], f, sort_keys=True, indent=4)

    def run_init(self):
	filename = self.find_file(Config.init_file)
	if filename is None:
	    return True

	nerve.log("running init script located at " + filename)
	try:
	    #execfile(filename, self.data, self.data)
	    global_dict = { 'nerve' : nerve }
	    execfile(filename, global_dict)
	    nerve.log(filename + " has completed sucessfully")
	    return True
	except:
	    nerve.log("error running init from " + filename + "\n\n" + traceback.format_exc())
	    return False

    def find_file(self, filename, all=False):
	filelist = [ ]
	for dir in self.path:
	    path = dir + '/' + filename
	    if os.path.exists(path):
		if all is False:
		    return path
		filelist.append(path)

	if all is False:
	    return None
	else:
	    return filelist

    def create_object(self, typename, name, *args):
	(modulename, dot, classname) = name.rpartition('.')
	module = self.import_module(modulename)
	objclass = getattr(module, classname)
	return objclass(*args)

    @staticmethod
    def import_module(modulename):
	try:
	    exec 'import %s as nervemodule' % (modulename,)
	    return locals()['nervemodule']
	except ImportError as e:
	    #nerve.log("error loading module " + modulename + "\n\n" + traceback.format_exc())
	    raise e

