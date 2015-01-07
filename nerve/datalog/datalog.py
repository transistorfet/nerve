# -*- coding: utf-8 -*-
#!/usr/bin/python

import nerve

import time
import os
import os.path
import traceback

import urllib
import random


class DatalogManager (nerve.Device):
    def __init__(self, **config):
	nerve.Device.__init__(self, **config)
	#self.dbconnection = nerve.Database('datalog.sqlite')
	#self.db = nerve.DatabaseCursor(self.dbconnection)
	#self.db.create_table('media', "id INTEGER PRIMARY KEY, filename TEXT, artist TEXT, album TEXT, title TEXT, track_num NUMERIC, genre TEXT, tags TEXT, duration NUMERIC, media_type TEXT, file_hash TEXT, file_size INT, file_last_modified INT")
	#self.db.create_table('info', "name TEXT PRIMARY KEY, value TEXT")

	if 'datalogs' not in config:
	    self.set_setting('datalogs', { })
	    self.datalogs = self.get_setting('datalogs')
	else:
	    self.datalogs = self.make_object_table(config['datalogs'])

	self.thread = nerve.Task("DatalogTask", target=self.run)
	self.thread.start()

    @staticmethod
    def get_config_info():
	config_info = nerve.ConfigObject.get_config_info()
	config_info.add_setting('datalogs', "Datalogs", default=dict())
	return config_info

    def get_config_data(self):
	config = nerve.ConfigObject.get_config_data(self)
	config['datalogs'] = self.save_object_table(self.datalogs)
	return config

    def add(self, name):
	if name in self.datalogs:
	    return False
	log = DatalogDevice(name=name)
	self.datalogs[name] = log
	return

    def run(self):
	while not self.thread.stopflag.wait(60):
	    try:
		for name in self.datalogs.keys():
		    self.datalogs[name]._collect_data()
	    except:
		nerve.log(traceback.format_exc())

    def __getattr__(self, name):
	if name not in self.datalogs:
	    raise AttributeException(name + " datalog not found")
	return self.datalogs[name]
	

class DatalogDevice (nerve.Device):
    def __init__(self, **config):
	nerve.Device.__init__(self, **config)
	self.name = config['name']

	self.db = nerve.Database.get_db('datalog.sqlite')
	self.db.create_table(self.name, "id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT")

	if 'datapoints' not in config:
	    self.set_setting('datapoints', [ ])

    def add_datapoint(self, column_name, ref, datatype="TEXT"):
	self.db.add_column(self.name, column_name, datatype)
	datapoints = self.get_setting('datapoints')
	datapoints.append([ column_name, ref ])

    def remove_datapoint(self, ref):
	pass

    def get_data(self, start_time=None, end_time=None):
	self.db.select('*')

	data = list(self.db.get_assoc(self.name))
	return data

    def _collect_data(self):
	data = { }
	data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
	for column_name, ref in self.get_setting('datapoints'):
	    data[column_name] = nerve.query(ref)
	self.db.insert(self.name, data)


