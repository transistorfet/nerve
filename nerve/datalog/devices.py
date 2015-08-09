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
        config_info.add_setting('datapoints', "Data Points", default=list(), iteminfo=datapoints_config)
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
        datapoints = self.get_setting('datapoints')
        datapoints.append(entry)

    def remove_datapoint(self, column_name):
        pass

    def get_datapoint_info(self, name):
        for datapoint in self.get_setting('datapoints'):
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
        for datapoint in self.get_setting('datapoints'):
            try:
                data[datapoint['name']] = nerve.query(datapoint['ref'])
            except Exception as exc:
                nerve.log("error collecting ref: " + str(datapoint['ref']) + ": " + repr(exc))
                data[datapoint['name']] = None
        self.db.insert(self.name, data)



