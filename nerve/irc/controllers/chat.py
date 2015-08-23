#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http
import nerve.connect
import nerve.medialib

import urllib
import urllib.parse

import json
import requests


class IRCChatController (nerve.http.Controller, nerve.connect.ControllerMixIn):
    def __init__(self, **config):
        super().__init__(**config)
        self.client = nerve.query('/devices/irc')

    def index(self, request):
        data = { }
        data['hostname'] = self.client.hostname
        data['linebuffer'] = list(self.client.linebuffer)
        self.load_template_view('nerve/irc/views/chat.blk.pyhtml', data, request)
        self.template_add_to_section('jsfiles', '/irc/assets/js/irc.js')
        self.template_add_to_section('cssfiles', '/irc/assets/css/irc.css')

    def connect(self, request):
        if request.reqtype != 'CONNECT':
            raise nerve.ControllerError("expected CONNECT request type; received " + request.reqtype)
        self.handle_connection(request)

    def on_connect(self):
        self.client.set_object('event_privmsg/'+str(id(self)), self.on_privmsg)

    def on_disconnect(self):
        self.client.del_object('event_privmsg/'+str(id(self)))

    def on_message(self, msg):
        msg.data = json.loads(msg.text)
        if msg.data['type'] == 'input':
            for line in msg.data['text'].split('\n'):
                self.client.sendprivmsg('#ircmoo', line.strip())

    def on_privmsg(self, msg):
        if hasattr(self, 'conn'):
            data = { }
            data['type'] = 'output'
            data['text'] = " [%s] %s\n" % (msg.nick, msg.text)
            self.conn.send_message(nerve.connect.Message(text=json.dumps(data)))

    def handle_connection_error(self, error, traceback):
        nerve.log(traceback)
        if self.conn:
            self.conn.send_message(nerve.connect.Message(text=traceback))


