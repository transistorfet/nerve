# -*- coding: utf-8 -*-
#!/usr/bin/python

import nerve
import nerve.http

import sys
import os.path
import traceback

import urllib
import urlparse


class DatalogController (nerve.http.Controller):

    def index(self, request):
	data = { }
	data['contents'] = nerve.get_config_file('html/remote.html')
	self.load_view('nerve/remote/views/index.pyhtml', data)

    def player(self, request):
	player = nerve.get_device('player')
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
	contents = nerve.get_config_file('html/remote.html')
	self.write_output(contents)

    def save_layout(self, request):
	try:
	    nerve.write_config_file('html/remote.html', request.arg('data', default=''))
	except:
	    result = { 'status' : 'error', 'message' : traceback.format_exc() }
	else:
	    result = { 'status' : 'success', 'message' : self.filename + ' saved successfully' }
	self.write_json(result)


