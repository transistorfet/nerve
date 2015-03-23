# -*- coding: utf-8 -*-
#!/usr/bin/python

import nerve
import nerve.http
import nerve.datalog

import sys
import os.path
import traceback

import urllib
import urllib.parse


class DatalogController (nerve.http.Controller):

    def index(self, request):
        # TODO redirect somehow to .../graph
        pass

    def graph(self, request):
        remain = request.remaining_segments().lstrip('/')
        # TODO if remain contains a / then raise an error

        datalogs = nerve.get_object('devices/datalogs')

        data = { }
        data['datalog_name'] = remain
        data['datalog_list'] = [ name for name in datalogs.keys() if isinstance(getattr(datalogs, name), nerve.datalog.DatalogDevice) ]
        self.load_view('nerve/datalog/views/graph.pyhtml', data)

    def get_data(self, request):
        datalog_name = request.args['datalog']
        start_time = request.args['start_time']
        length = request.args['length']
        ref = 'datalogs/%s/get_data' % (datalog_name,)

        data = nerve.query(ref, start_time=start_time, length=length)
        self.write_json(data)


