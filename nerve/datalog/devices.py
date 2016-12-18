#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import os
import os.path
import traceback

import urllib
import random


class DatalogDevice (nerve.Device):
    datalogs = [ ]

    def __init__(self, **config):
        super().__init__(**config)
        self.name = self.get_setting('name')

        self.db = nerve.Database('datalog.sqlite')
        table_sql = "id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp NUMERIC"
        for datapoint in self.get_setting('datapoints'):
            table_sql += ", %s %s" % (datapoint['name'], datapoint['datatype'])
        self.db.create_table(self.name, table_sql)

        column_names = [ column[1] for column in self.db.get_column_info(self.name) ]
        for datapoint in self.get_setting('datapoints'):
            if datapoint['name'] not in column_names:
                self.db.add_column(self.name, datapoint['name'], datapoint['datatype'], default='')

        DatalogDevice.datalogs.append(self)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('name', "Table Name", default='')
        config_info.add_setting('update_time', "Update Time", default=60.0)

        datapoints_config = nerve.types.StructConfigType()
        datapoints_config.add_setting('name', "Column Name", default='')
        datapoints_config.add_setting('ref', "Target URI", default='')
        datapoints_config.add_setting('datatype', "Data Type", default='')
        datapoints_config.add_setting('label', "Label", default='')
        datapoints_config.add_setting('min', "Minimum Value", default=0.0)
        datapoints_config.add_setting('max', "Maximum Value", default=0.0)
        datapoints_config.add_setting('units', "Units", default='')
        config_info.add_setting('datapoints', "Data Points", default=list(), itemtype=datapoints_config)
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
        datapoints = self.get_setting('datapoints')
        datapoints.append(entry)
        # TODO I guess the config needs to be updated somehow

    def remove_datapoint(self, column_name):
        for (i, datapoint) in enumerate(self.get_setting('datapoints')):
            if datapoint['name'] == column_name:
                # TODO finish this
                return

    def get_datapoint_info(self, name):
        for datapoint in self.get_setting('datapoints'):
            if name == datapoint['name']:
                return datapoint
        return { 'name': name }

    def get_data(self, start_time=None, length=None):
        columns = [ datapoint['name'] for datapoint in self.get_setting('datapoints') ]
        self.db.select('timestamp,' + ','.join(columns))
        if start_time != None:
            self.db.where_gt('timestamp', start_time)
            if length != None:
                self.db.where_lt('timestamp', start_time + length)
        result = self.db.get(self.name)

        #columns = [ ]
        #for column in self.db.get_columns():
        #    columns.append(self.get_datapoint_info(column[0]))
        return { 'columns' : [{ 'name': 'timestamp' }] + self.get_setting('datapoints'), 'data' : list(result) }

    def _collect_data(self):
        data = { }
        data['timestamp'] = time.time()
        for datapoint in self.get_setting('datapoints'):
            try:
                data[datapoint['name']] = nerve.query(datapoint['ref'])
            except Exception as exc:
                nerve.log("error collecting ref: " + str(datapoint['ref']) + ": " + repr(exc), logtype='error')
                data[datapoint['name']] = None
        self.db.insert(self.name, data)

    def __getattr__(self, index):
        for datapoint in self.get_setting('datapoints'):
            if datapoint['name'] == index:
                return DatalogReference(db=self.db, dbtable=self.name, **datapoint)
        return super().__getattr__(index)

    def keys_queries(self):
        return super().keys_queries() + [ datapoint['name'] for datapoint in self.get_setting('datapoints') ]


# TODO we had to make this inherit from ObjectNode because the nerve.query function uses obj.query to access data... not sure if this is good
class DatalogReference (nerve.ObjectNode):
    def __init__(self, **datapoint):
        for attrib in datapoint:
            setattr(self, attrib, datapoint[attrib])

    def __call__(self):
        return nerve.query(self.ref)

    def calc(self, start=None, length=86400, function='AVG'):
        length = self._get_time_value(length)
        if start == None:
            start = time.time() - length
        else:
            start = self._get_time_value(start)
            if start < 0:
                start = time.time() - start
        self.db.select("{0}({1}) AS {1}".format(function, self.name))
        self.db.where_gt('timestamp', start)
        self.db.where_lt('timestamp', start + length)
        data = self.db.get_first_row(self.dbtable)
        return data[0] if data else None

    @staticmethod
    def _get_time_value(value):
        if type(value) == str:
            factor = 60 if value[-1] == 'm' else 3600 if value[-1] == 'h' else 86400 if value[-1] == 'd' else 604800 if value[-1] == 'w' else 1
            return int(float(value if factor == 1 else value[:-1]) * factor)
        else:
            return int(value)

    def average(self, start=None, length=86400):
        return self.calc(start, length, 'AVG')

    def low(self, start=None, length=86400):
        return self.calc(start, length, 'MIN')

    def high(self, start=None, length=86400):
        return self.calc(start, length, 'MAX')

