#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http
import nerve.datalog

import sys
import os.path
import traceback

import urllib
import urllib.parse


class DatalogController (nerve.http.Controller):

    def handle_error(self, error, traceback):
        if type(error) == nerve.NotFoundError or self.get_mimetype() != None:
            super().handle_error(error, traceback)
        else:
            self.load_json_view({ 'status' : 'error', 'message' : repr(error) })

    @nerve.public
    def index(self, request):
        self.redirect_to('/%s/graph' % (request.segments[0],))

    @nerve.public
    def graph(self, request):
        remain = request.get_remaining_segments().lstrip('/')
        # TODO if remain contains a / then raise an error

        datalogs = nerve.get_object('/devices/datalogs')

        data = { }
        data['datalog_name'] = remain
        data['datalog_list'] = [ name for name in datalogs.keys_children() if isinstance(getattr(datalogs, name), nerve.datalog.DatalogDevice) ]
        self.load_template_view('nerve/datalog/views/graph.blk.pyhtml', data, request)
        self.template_add_to_section('jsfiles', '/datalog/assets/js/datalog.js')
        self.template_add_to_section('cssfiles', '/datalog/assets/css/datalog.css')

    @nerve.public
    def get_data(self, request):
        datalog_name = request.args['datalog']
        start_time = request.args['start_time']
        length = request.args['length']
        ref = '/devices/datalogs/%s/get_data' % (datalog_name,)

        data = nerve.query(ref, start_time=start_time, length=length)
        self.load_json_view(data)


