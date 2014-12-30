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

if sys.version.startswith('3'):
    from urllib.parse import parse_qs,urlparse
else:
    from urlparse import parse_qs,urlparse


class HTTPRequestHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "Nerve HTTP/0.2"

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

	if not self.is_valid_path(self.path):
	    self.send_404()

	request = nerve.Request(self, 'GET', self.path, None)
	#url = urlparse(self.path)
	request.args = parse_qs(request.url.query)
	self.do_request(request)

    def do_POST(self):
        if self.check_authorization() == False:
            return

	if not self.is_valid_path(self.path):
	    self.send_404()

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

	request = nerve.Request(self, 'POST', self.path, postvars)
	self.do_request(request)

    def do_request(self, request):
	controller = self.server.find_controller(request)
	success = controller.handle_request(request)
	# TODO fetch the error from the controller
	self.send_headers(200 if success else 404, controller.get_mimetype())
	self.wfile.write(controller.get_output())
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

    @staticmethod
    def is_valid_path(path):
	if not path[0] == '/':
	    return False
	for name in path.split('/'):
	    if name == '.' or name == '..':
		return False
	return True


class HTTPServer (nerve.Server, BaseHTTPServer.HTTPServer):
    def __init__(self, **config):
	nerve.Server.__init__(self, **config)
	self.root = 'nerve/http/wwwdata'

        self.username = self.get_setting("username")
        self.password = self.get_setting("password")

        #sslenable = obplayer.Config.setting('http_admin_secure')
        #sslcert = obplayer.Config.setting('http_admin_sslcert')

        #server_address = ('', obplayer.Config.setting('http_admin_port'))  # (address, port)

	BaseHTTPServer.HTTPServer.__init__(self, ('', config['port']), HTTPRequestHandler)
	#if sslenable:
	#    self.socket = ssl.wrap_socket(self.socket, certfile=sslcert, server_side=True)

        sa = self.socket.getsockname()
        nerve.log('starting http(s) on port ' + str(sa[1]))

	self.thread = nerve.Task('HTTPServerTask', target=self.serve_forever)
	self.thread.daemon = True
	self.thread.start()

    @staticmethod
    def get_defaults():
	defaults = nerve.Server.get_defaults()
	defaults['port'] = 8888
	defaults['controllers']['__default__'] = {
	    'type' : 'base/ConfigController',
	    'username' : 'admin',
	    'password' : 'admin'
	}
	return defaults


    @staticmethod
    def register_config():
	self.register_server('http/HTTPServer', HTTPServer)
	self.register_setting('port', 'Port', 8888)

