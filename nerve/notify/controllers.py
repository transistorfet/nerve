#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http
import nerve.medialib

import urllib
import urllib.parse

import json
import requests


class NotifyController (nerve.http.Controller):

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('device', "Notify Device", default='/devices/notify')
        return config_info

    @nerve.public
    def index(self, request):
        data = { }
        self.load_template_view('nerve/notify/views/list.blk.pyhtml', data, request)
        self.template_add_to_section('jsfiles', '/notify/assets/js/notify.js')
        #self.template_add_to_section('cssfiles', '/notify/assets/css/notify.css')

    @nerve.public
    def list(self, request):
        notify = nerve.get_object(self.get_setting('device'))

        data = { }
        data['notifications'] = notify.list()
        self.load_html_view('nerve/notify/views/list-data.blk.pyhtml', data)

    @nerve.public
    def acknowledge(self, request):
        if not request.arg('nids[]'):
            raise nerve.ControllerError("'nids[]' field must be set")

        notify = nerve.get_object(self.get_setting('device'))
        for nid in request.arg('nids[]'):
            notify.acknowledge(int(nid))
        self.load_json_view(True)

    @nerve.public
    def acknowledge_all(self, request):
        notify = nerve.get_object(self.get_setting('device'))
        notify.acknowledge(-1)
        self.load_json_view(True)

    @nerve.public
    def clear(self, request):
        if not request.arg('nids[]'):
            raise nerve.ControllerError("'nids[]' field must be set")

        notify = nerve.get_object(self.get_setting('device'))
        for nid in request.arg('nids[]'):
            notify.clear(int(nid))
        self.load_json_view(True)

    @nerve.public
    def clear_all(self, request):
        notify = nerve.get_object(self.get_setting('device'))
        notify.clear(-1)
        self.load_json_view(True)

