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

    @nerve.public
    def index(self, request):
        data = { }
        #data['contents'] = nerve.load_file('html/remote.html')
        data['contents'] = self.make_html_view(nerve.configdir() + '/html/remote.html')
        self.load_html_view('nerve/remote/views/index.pyhtml', data)

    # TODO this is temporary
    @nerve.public
    def summary(self, request):
        data = { }
        data['contents'] = nerve.load_file('html/summary.html')
        self.load_html_view('nerve/remote/views/index.pyhtml', data)

    @nerve.public
    def player(self, request):
        player = nerve.get_object('/devices/player')
        if request.reqtype == "POST":
            if 'play' in request.args:
                player.playlist_seek(request.arg('play'))
        else:
            data = { }
            data['playlist'] = player.getplaylist()
            self.load_html_view('nerve/remote/views/player.pyhtml', data)

    @nerve.public
    def edit_layout(self, request):
        data = { }
        self.load_html_view('nerve/remote/views/editor.pyhtml', data)

    @nerve.public
    def get_layout(self, request):
        self.load_file_view('html/remote.html', base=nerve.configdir())

    @nerve.public
    def save_layout(self, request):
        try:
            nerve.save_file('html/remote.html', request.arg('data', default=''))
        except:
            result = { 'status' : 'error', 'message' : traceback.format_exc() }
        else:
            result = { 'status' : 'success', 'message' : 'Remote layout saved successfully' }
        self.load_json_view(result)

    @nerve.public
    def voice(self, request):
        text = request.arg('text').lower()
        nerve.log("executing voice command: " + text)
        words = text.split()

        if text == 'play':
            nerve.query("player/toggle")
        elif text == 'next':
            nerve.query("player/next")
        elif text == 'previous':
            nerve.query("player/previous")
        else:
            if words[-1] in [ 'on', 'off' ]:
                for word in words[:-1]:
                    try:
                        if word in [ 'tv', 'stereo', 'rgb' ]:
                            nerve.query(word + "/power")
                        elif word == 'lamp':
                            nerve.query("sensors/relay_toggle")
                        elif word == 'player':
                            nerve.query("player/toggle")
                    except:
                        pass


