#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import socket
import os
import sys
import signal
import traceback

import SocketServer
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
    protocol_version = 'HTTP/1.1'
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

        content = 'Authorization required.'
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Secure Area"')
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)
        return False

    def do_GET(self):
        if self.check_authorization() == False:
            return

        if not self.is_valid_path(self.path):
            self.send_404()

        request = nerve.Request(self, 'GET', self.path, None)
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
        self.send_content(200 if success else 404, controller.get_mimetype(), controller.get_output())
        return

    def send_content(self, errcode, mimetype, content):
        self.send_response(errcode)
        self.send_header('Content-Type', mimetype)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def send_400(self):
        self.send_content(400, 'text/plain', '400 Bad Request')

    def send_404(self):
        self.send_content(404, 'text/plain', '404 Not Found')

    @staticmethod
    def is_valid_path(path):
        if not path[0] == '/':
            return False
        for name in path.split('/'):
            if name == '.' or name == '..':
                return False
        return True


class HTTPServer (nerve.Server, SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):  #, SocketServer.ThreadingMixIn
    daemon_threads = True

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
    def get_config_info():
        config_info = nerve.Server.get_config_info()
        config_info.add_setting('port', "Port", default=8888)
        config_info.add_setting('username', "Username", default='')
        config_info.add_setting('password', "Password", default='')
        return config_info


