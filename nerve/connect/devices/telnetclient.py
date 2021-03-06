#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.connect

import os
import sys
import time
import socket
import string
import traceback

class TelnetClient (nerve.Device, nerve.connect.Connection):
    version = "0.1"
    start_time = time.time()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('hostname', "Hostname", default='')
        config_info.add_setting('port', "Port", default=6667)
        return config_info

    def __init__(self, **config):
        super().__init__(**config)
        self.connected = False
        self.socket = None
        self.hostname = None
        self.port = 0
        self.lastcontact = time.time()
        self.linebuffer = [ ]
        self.callbacks = [ ]
        if not self.get_child('event_message'):
            self.set_child('event_message', nerve.ObjectNode.make_object('objects/ObjectNode', dict()))

        self.thread = TelnetClientThread(self)
        self.thread.start()

    def connect(self, hostname, port):
        if self.socket:
            self.close()

        self.connected = False
        self.hostname = hostname
        self.port = int(port)
        self.socket = socket.create_connection((hostname, int(port)))
        self.rfile = self.socket.makefile(mode='r', encoding='utf-8', newline='\n')
        self.connected = True

    def close(self):
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.socket.close()
            self.connected = False

    def read_message(self, mimetype='text/plain'):
        # TODO should you check mimetype and die if not text?
        line = self.rfile.readline()
        if not line:
            return None
        line = line.rstrip('\r\n')
        nerve.log(" IN: " + line)
        return nerve.connect.Message(text=line + '\n', mimetype=mimetype)

    def send_message(self, msg):
        text = msg.text.rstrip()
        nerve.log("OUT: " + repr(text))
        self.socket.send(bytes(text + '\n', 'utf-8'))

    def dispatch(self, msg):
        self.linebuffer.append(msg.text.rstrip())
        if len(self.linebuffer) > 100:
            self.linebuffer = self.linebuffer[len(self.linebuffer) - 100:]
        self.query('event_message/*', msg)

    @nerve.public
    def connected(self):
        return self.connected

    @nerve.public
    def address(self):
        return self.hostname + ":" + str(self.port)


class TelnetClientThread (nerve.Thread):
    def __init__(self, client):
        super().__init__('TelnetClientThread')
        self.client = client

    def connect_any(self):
        while not self.stopflag.is_set():
            hostname = self.client.get_setting('hostname')
            port = self.client.get_setting('port')
            #url = urllib.parse.urlparse(address)
            try:
                nerve.log("connecting to " + hostname + ":" + str(port))
                self.client.connect(hostname, port)
                return

            except OSError as e:
                nerve.log("error connecting to " + hostname + ":" + port + ": " + str(e), logtype='error')
            self.stopflag.wait(10)

    def run(self):
        while not self.stopflag.is_set():
            self.connect_any()

            while not self.stopflag.is_set():
                try:
                    msg = self.client.read_message()
                    if msg == None:
                        break
                    self.client.lastcontact = time.time()
                    self.client.dispatch(msg)
                except:
                    nerve.log("error on telnet connection to " + self.client.hostname + ":" + str(self.client.port), logtype='error')
                    nerve.log(traceback.format_exc(), logtype='error')
                    break
            self.client.close()
            self.stopflag.wait(10)

    def stop(self):
        self.client.close()
        super().stop()


