#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import socket
import os
import sys
import signal
import traceback

import BaseHTTPServer
import ssl

import cgi
import json
import mimetypes

from nerve.http import pyhtml

if sys.version.startswith('3'):
    from urllib.parse import parse_qs,urlparse
else:
    from urlparse import parse_qs,urlparse


class HTTPRequestHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "Nerve HTTP/0.1"

    def log_message(self, format, *args):
        nerve.log(self.address_string() + ' ' + format % args)

    def check_authorization(self):
	if not self.server.username:
	    return True

        authdata = self.headers.getheader('Authorization')
        if type(authdata).__name__ == 'str':
            authdata = authdata.split(' ')[-1].decode('base64')
            username = authdata.split(':')[0]
            password = authdata.split(':')[1]

            if username == self.server.username and password == self.server.password:
                return True

	self.send_response(401)
	self.send_header('WWW-Authenticate', 'Basic realm="Secure Area"')
	self.send_header('Content-type', 'text/html')
	self.end_headers()
	self.wfile.write('Authorization required.')
        return False

    def do_GET(self):
        if self.check_authorization() == False:
            return
	url = urlparse(self.path)
	return self.do_request("GET", url, parse_qs(url.query))

    def do_POST(self):
        if self.check_authorization() == False:
            return

	# empty post doesn't provide a content-type.
	ctype = None
        try:
            (ctype, pdict) = cgi.parse_header(self.headers['content-type'])
        except:
	    pass

        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(self.rfile.read(length), keep_blank_values=True)
        else:
            postvars = {}

	url = urlparse(self.path)
	if url.path == '/query':
	    print "Vars: " + repr(postvars)
	    if 'tag' not in postvars:
		self.send_400()
		return
	    self.send_json_headers()
	    result = nerve.query(postvars['tag'][0])
	    self.wfile.write(json.dumps(result))
	else:
	    return self.do_request("POST", url, postvars)

	"""
	elif path[0] == '/':
	    devname, sep, cmdname = path.rpartition('/')
	    devname = devname[1:].replace('/', '.')
	    dev = nerve.get_device(devname)
	    if dev is not None:
		func = getattr(dev, 'html_' + cmdname)
		return func(postvars)
	    else:
		return { 'error' : 1 }
	"""

    def do_request(self, reqtype, url, params=None):
	if not self.is_valid_path(url.path):
	    self.send_404()
	    return

	# TODO debugging: remove later
	print "Path: " + url.path
	print "Vars: " + repr(params)

	filename = os.path.join(self.server.root, url.path[1:])

	# If the path resolves to a directory, then set the filename to the index.html file inside that directory
	if os.path.isdir(filename):
	    filename = filename.strip('/') + '/index.html'

	# send error if nothing found
	if not os.path.isfile(filename):
	    self.send_404()
	    return

	# server up the file
	(self.mimetype, self.encoding) = mimetypes.guess_type(filename)
	self.send_headers(200, self.mimetype)

	with open(filename, 'r') as f:
	    contents = f.read()

	    if self.mimetype == 'text/html' or self.mimetype == 'text/xml' or self.mimetype == 'application/json':
		interp = pyhtml.PyHTMLParser(contents, filename=filename, reqtype=reqtype, path=url.path, params=params)
		contents = interp.evaluate()
	    self.wfile.write(contents)
	return

    def send_headers(self, errcode, mimetype, content=None):
	self.send_response(errcode)
	self.send_header('Content-type', mimetype)
	self.end_headers()
        if content is not None:
	    self.wfile.write(content)

    def send_400(self):
        self.send_headers(400, 'text/plain', '400 Bad Request')

    def send_404(self):
        self.send_headers(404, 'text/plain', '404 Not Found')

    def send_json_headers(self):
        self.send_headers(200, 'application/json')

    @staticmethod
    def is_valid_path(path):
	if not path[0] == '/':
	    return False
	for name in path.split('/'):
	    if name == '.' or name == '..':
		return False
	return True


class HTTPServer (nerve.Portal, BaseHTTPServer.HTTPServer):

    def __init__(self, port):
	self.root = 'wwwdata'

        self.username = None #obplayer.Config.setting('http_admin_username')
        self.password = None #obplayer.Config.setting('http_admin_password')

        #sslenable = obplayer.Config.setting('http_admin_secure')
        #sslcert = obplayer.Config.setting('http_admin_sslcert')

        #server_address = ('', obplayer.Config.setting('http_admin_port'))  # (address, port)

	BaseHTTPServer.HTTPServer.__init__(self, ('', port), HTTPRequestHandler)
	#if sslenable:
	#    self.socket = ssl.wrap_socket(self.socket, certfile=sslcert, server_side=True)

        sa = self.socket.getsockname()
        nerve.log('starting http(s) on port ' + str(sa[1]))

	self.thread = nerve.Task('HTTPServerTask', target=self.serve_forever)
	self.thread.daemon = True
	self.thread.start()


