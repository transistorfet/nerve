# -*- coding: utf-8 -*-
#!/usr/bin/python

import nerve
import nerve.http

import urllib
import urlparse


class RemoteController (nerve.http.Controller):

    def index(self, request):
	data = { }
	self.load_view('nerve/remote/views/index.pyhtml', data)

    def player(self, request):
	player = nerve.get_device('player')
	if request.reqtype == "POST":
	    if 'play' in request.args:
		player.playlist_seek(request.arg('play'))
	else:
	    data = { }
	    data['playlist'] = player.getplaylist(None)
	    self.load_view('nerve/remote/views/player.pyhtml', data)

