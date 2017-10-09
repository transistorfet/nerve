#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import time
import socket
import select
import traceback

import hashlib
import base64

import cgi
import json
import mimetypes

import urllib.parse

from ..msg import Colours, MsgType, Msg

import socketserver


# TODO this is the skeleton for an irc server server
class IRCServerRequestHandler(socketserver.StreamRequestHandler):

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        self.data = self.rfile.readline().strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        self.wfile.write(self.data.upper())


class IRCServer (nerve.Server, socketserver.TCPServer):
    daemon_threads = True

    def __init__(self, **config):
        nerve.Server.__init__(self, **config)

        self.username = self.get_setting("username")
        self.password = self.get_setting("password")

        socketserver.TCPServer.__init__(self, ('', self.get_setting('port')), IRCRequestHandler)
        #if self.get_setting('ssl_enable'):
        #    self.socket = ssl.wrap_socket(self.socket, certfile=self.get_setting('ssl_cert'), server_side=True)

        sa = self.socket.getsockname()
        nerve.log('starting http(s) on port ' + str(sa[1]))

        self.thread = nerve.Thread('HTTPServerThread', target=self.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        return config_info


