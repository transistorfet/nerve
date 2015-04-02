#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

import sys
import os.path
import traceback

import urllib
import urllib.parse


class RemoteController (nerve.http.Controller):

    def index(self, request):
        data = { }
        data['contents'] = nerve.read_config_file('html/remote.html')
        self.load_view('nerve/remote/views/index.pyhtml', data)

    def player(self, request):
        player = nerve.get_object('devices/player')
        if request.reqtype == "POST":
            if 'play' in request.args:
                player.playlist_seek(request.arg('play'))
        else:
            data = { }
            data['playlist'] = player.getplaylist()
            self.load_view('nerve/remote/views/player.pyhtml', data)

    def edit_layout(self, request):
        data = { }
        self.load_view('nerve/remote/views/editor.pyhtml', data)

    def get_layout(self, request):
        contents = nerve.read_config_file('html/remote.html')
        self.write_text(contents)

    def save_layout(self, request):
        try:
            nerve.write_config_file('html/remote.html', request.arg('data', default=''))
        except:
            result = { 'status' : 'error', 'message' : traceback.format_exc() }
        else:
            result = { 'status' : 'success', 'message' : 'Remote layout saved successfully' }
        self.write_json(result)

    def voice(self, request):
        text = request.arg('text').lower()
        nerve.log("executing voice command: " + text)
        words = text.split()

        if text == 'play':
            nerve.query_string("player/toggle")
        elif text == 'next':
            nerve.query_string("player/next")
        elif text == 'previous':
            nerve.query_string("player/previous")
        else:
            if words[-1] in [ 'on', 'off' ]:
                for word in words[:-1]:
                    try:
                        if word in [ 'tv', 'stereo', 'rgb' ]:
                            nerve.query_string(word + "/power")
                        elif word == 'lamp':
                            nerve.query_string("sensors/relay_toggle")
                        elif word == 'player':
                            nerve.query_string("player/toggle")
                    except:
                        pass


