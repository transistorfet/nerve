# -*- coding: utf-8 -*-
#!/usr/bin/python

import nerve
import nerve.http

import sys
import os.path
import traceback

import urllib
import urlparse


class RemoteController (nerve.http.Controller):
    def __init__(self, **config):
	nerve.http.Controller.__init__(self, **config)
	htmlroot = nerve.configdir() + '/html'
	if not os.path.isdir(htmlroot):
	    os.mkdir(htmlroot)
	self.filename = htmlroot + "/remote.html"
	if not os.path.isfile(self.filename):
	    with open(self.filename, 'w'):
		pass

    def index(self, request):
	data = { }
	with open(self.filename, 'r') as f:
	    data['contents'] = f.read()
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

    def edit_layout(self, request):
	data = { }
	self.load_view('nerve/remote/views/editor.pyhtml', data)

    def get_layout(self, request):
	with open(self.filename, 'r') as f:
	    self.write_output(f.read())

    def save_layout(self, request):
	try:
	    data = request.arg('data')
	    with open(self.filename, 'w') as f:
		f.write(data)
	except:
	    result = { 'status' : 'error', 'message' : traceback.format_exc() }
	else:
	    result = { 'status' : 'success', 'message' : self.filename + ' saved successfully' }
	self.write_json(result)


