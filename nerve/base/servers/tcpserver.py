#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import socket
import thread
import sys
import os
import traceback
import string


class TCPConnection (nerve.Server):
    def __init__(self, server, socket, addr, controllers):
        nerve.Server.__init__(self)
	self.server = server
	self.socket = socket
	(self.host, self.port) = addr
        self.controllers = controllers

	self.buffer = ""

	self.thread = nerve.Task('TCPConnectionTask', self.run)
	self.thread.daemon = True
	self.thread.start()

    def readline(self):
	while 1:
	    if self.buffer:
		i = self.buffer.find('\n')
		if i >= 0:
		    line = self.buffer[:i].strip('\n\r')
		    self.buffer = self.buffer[i+1:]
		    return line
	    data = self.socket.recv(4096)
	    if not data:
		raise socket.error("TCP socket closed by remote end. (" + str(self.host) + ":" + str(self.port) + ")")
	    self.buffer = self.buffer + data

    def send(self, data):
	nerve.log("SEND -> " + str(self.host) + ":" + str(self.port) + ": " + data)
	self.socket.send(data + '\n')

    def close(self):
        nerve.log("closing connection to " + str(self.host) + ":" + str(self.port))
	self.socket.close()

    def run(self):
	while not self.thread.stopflag.is_set():
	    try:
		data = self.readline()
		data = data.strip('\n')
		if data:
		    nerve.log("RECV <- " + str(self.host) + ":" + str(self.port) + ": " + data)

                    if data == 'quit':
                        self.thread.stopflag.set()
                    else:
                        request = nerve.Request(self, 'QUERY', "", { 'queries[]' : [ data ] })
                        controller = self.find_controller(request)
                        controller.handle_request(request)
                        self.send(controller.get_output() + '\n')

	    except socket.error, e:
		nerve.log("Socket Error: " + str(e))
		break

	    except:
		nerve.log(traceback.format_exc())
	self.close()
        self.thread.finish()


class TCPServer (nerve.Server):
    def __init__(self, **config):
        nerve.Server.__init__(self, **config)

	self.thread = nerve.Task('TCPServerTask', self.run)
	self.thread.daemon = True
	self.thread.start()

    @staticmethod
    def get_config_info():
	config_info = nerve.Server.get_config_info()
        config_info.add_setting('port', "Port", default=12345)
	config_info.add_setting('controllers', "Controllers", default={
	    '__default__' : {
		'type' : 'base/ShellController'
	    }
	})
	return config_info

    def listen(self):
        nerve.log("starting tcp server on port " + str(self.port))
	self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	self.socket.bind(('', self.port))
	self.socket.listen(5)

    def close(self):
	self.running = 0;
	self.socket.close()

    def run(self):
	while not self.thread.stopflag.is_set():
	    self.listen()
	    while not self.thread.stopflag.is_set():
		try:
		    sock, addr = self.socket.accept()
		    conn = TCPConnection(self, sock, addr, self.controllers)

		except socket.error, e:
		    nerve.log("Socket Error: " + str(e))
		    break

		except:
		    nerve.log(traceback.format_exc())

	    nerve.log("closing socket and retrying in 5 seconds")
	    self.socket.close()
	    time.sleep(5)


