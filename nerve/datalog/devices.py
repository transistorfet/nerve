#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
        #self.db = nerve.Database('datalog.sqlite')
        #self.db.create_table('media', "id INTEGER PRIMARY KEY, filename TEXT, artist TEXT, album TEXT, title TEXT, track_num NUMERIC, genre TEXT, tags TEXT, duration NUMERIC, media_type TEXT, file_hash TEXT, file_size INT, file_last_modified INT")
        #self.db.create_table('info', "name TEXT PRIMARY KEY, value TEXT")

        self.thread = nerve.Task("DatalogTask", target=self.run)
        self.thread.start()

    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        return config_info

    def add(self, name, update_time=60):
        log = DatalogDevice(name=name, update_time=update_time)
        nerve.set_device('name', log)
        return

    def run(self):
        while not self.thread.stopflag.wait(60):
            try:
                datalogs = nerve.get_object('devices/datalogs')
                for name in datalogs.keys():
                    obj = getattr(datalogs, name)
                    if isinstance(obj, DatalogDevice):
                        obj._collect_data()
            except:
                nerve.log(traceback.format_exc())


class DatalogDevice (nerve.Device):
    def __init__(self, **config):
        nerve.Device.__init__(self, **config)

        self.db = nerve.Database('datalog.sqlite')
        table_sql = "id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp NUMERIC"
        for datapoint in self.datapoints:
            table_sql += ", %s %s" % (datapoint['name'], datapoint['datatype'])
        self.db.create_table(self.name, table_sql)

    @staticmethod
    def get_config_info():
        config_info = nerve.Device.get_config_info()
        config_info.add_setting('name', "Table Name", default='')
        config_info.add_setting('datapoints', "Data Points", default=list())
        config_info.add_setting('update_time', "Update Time", default=60.0)

        """
        datapoints_config = nerve.ConfigInfo()
        datapoints_config.add_setting('name', "Column Name", default='')
        datapoints_config.add_setting('ref', "Target URI", default='')
        datapoints_config.add_setting('datatype', "Data Type", default='')
        datapoints_config.add_setting('label', "Label", default='')
        datapoints_config.add_setting('min', "Minimum Value", default=0.0)
        datapoints_config.add_setting('max', "Maximum Value", default=0.0)
        datapoints_config.add_setting('units', "Units", default='')
        config_info.add_setting('datapoints', "Data Points", default=list(datapoints_config))
        """
        return config_info

    def add_datapoint(self, column_name, ref, datatype="TEXT", label=None, rangemin=0, rangemax=100, units=''):
        if label is None:
            label = column_name

        entry = {
            'name' : column_name,
            'ref' : ref,
            'datatype' : datatype,
            'label' : label,
            'min' : rangemin,
            'max' : rangemax,
            'units' : units
        }

        self.db.add_column(self.name, column_name, datatype)
        self.datapoints.append(entry)

    def remove_datapoint(self, column_name):
        pass

    def get_datapoint_info(self, name):
        for datapoint in self.datapoints:
            if name == datapoint['name']:
                return datapoint
        return { 'name': name }

    def get_data(self, start_time=None, length=None):
        self.db.select('*')
        if start_time is not None:
            self.db.where_gt('timestamp', start_time)
        result = self.db.get(self.name)

        columns = [ ]
        for column in self.db.get_columns():
            columns.append(self.get_datapoint_info(column[0]))
        return { 'columns' : columns, 'data' : list(result) }

    def _collect_data(self):
        data = { }
        #data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
        data['timestamp'] = time.time()
        for datapoint in self.datapoints:
            data[datapoint['name']] = nerve.query(datapoint['ref'])
        self.db.insert(self.name, data)


