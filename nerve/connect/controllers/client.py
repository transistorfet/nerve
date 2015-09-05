#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http
import nerve.connect

import io
import shlex


class ClientController (nerve.http.Controller, nerve.connect.ControllerMixIn):
    def __init__(self, **config):
        super().__init__(**config)
        self.client = nerve.query('/devices/lambdamoo')

    def initialize(self, request):
        super().initialize(request)
        self.client.set_object('event_message/'+str(id(self)), self.send_message)

    def finalize(self, request):
        super().finalize(request)
        self.client.del_object('event_message/'+str(id(self)))

    @nerve.public
    def index(self, request):
        if request.reqtype == 'CONNECT':
            self.handle_connection(request)
        else:
            data = { }
            #data['hostname'] = self.server.hostname
            data['linebuffer'] = list(self.client.linebuffer)
            self.load_template_view('nerve/connect/views/client.blk.pyhtml', data, request)

    def on_message(self, msg):
        self.conn.send_message(msg)
        self.client.send_message(msg)

    def send_message(self, msg):
        if hasattr(self, 'conn'):
            self.conn.send_message(msg)

    def handle_connection_error(self, error, traceback):
        nerve.log(traceback)
        self.send_message(traceback)

