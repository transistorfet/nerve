#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import socket
import os
import sys
import signal
import traceback

import socketserver
import http.server
import base64
import ssl

import cgi
import json
import mimetypes

import urllib.parse


class HTTPRequestHandler (http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    server_version = "Nerve HTTP/0.2"

    def log_message(self, format, *args):
        nerve.log(self.address_string() + ' ' + format % args)

    def check_authorization(self):
        if not self.server.username:
            return True

        authdata = self.headers.get('Authorization')
        if authdata:
            (username, _, password) = base64.b64decode(bytes(authdata.split(' ')[-1], 'utf-8')).decode('utf-8').partition(':')
            if username == self.server.username and password == self.server.password:
                return True

        self.send_content(401, 'text/html', 'Authorization required.', [ ('WWW-Authenticate', 'Basic realm="Secure Area"') ])
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
            qstr = self.rfile.read(length).decode('utf-8')
            postvars = urllib.parse.parse_qs(qstr, keep_blank_values=True)
        else:
            postvars = {}

        request = nerve.Request(self, 'POST', self.path, postvars)
        self.do_request(request)

    def do_request(self, request):
        controller = self.server.make_controller(request)
        controller.handle_request(request)

        mimetype = controller.get_mimetype()
        redirect = controller.get_redirect()
        error = controller.get_error()
        output = controller.get_output()

        if redirect:
            self.send_content(302, mimetype, output, [ ('Location', redirect) ])
        else:
            self.send_content(200 if not error else 404, mimetype, output)
        return

    def send_content(self, errcode, mimetype, content, headers=None):
        if isinstance(content, str):
            content = bytes(content, 'utf-8')
        self.send_response(errcode)
        self.send_header('Content-Type', mimetype)
        self.send_header('Content-Length', len(content))
        if headers:
            for (header, value) in headers:
                self.send_header(header, value)
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


class HTTPServer (nerve.Server, socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

    def __init__(self, **config):
        nerve.Server.__init__(self, **config)

        self.username = self.get_setting("username")
        self.password = self.get_setting("password")

        http.server.HTTPServer.__init__(self, ('', self.get_setting('port')), HTTPRequestHandler)
        #if self.get_setting('ssl_enable'):
        #    self.socket = ssl.wrap_socket(self.socket, certfile=self.get_setting('ssl_cert'), server_side=True)

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
        config_info.add_setting('ssl_enable', "SSL Enable", default=False)
        config_info.add_setting('ssl_cert', "SSL Certificate File", default='')
        return config_info


