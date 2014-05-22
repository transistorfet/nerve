#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import socket
import thread
import sys
import os
import time
import traceback
import string

class UDPNetworkPortal (nerve.Portal):
    def __init__(self, server, addr):
	self.server = server
	self.addr = addr

    def send(self, text):
	self.server.send(text, self.addr)


class UDPServer (nerve.Portal, nerve.Task):
    def __init__(self, port):
	nerve.Task.__init__(self, 'UDPServerTask')
	self.daemon = True

	self.port = port

	self.start()

    def open(self):
	self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	self.socket.bind(('', self.port))

    def close(self):
	addr, port = self.socket.getsockname()
	nerve.log("closing socket %s:%s" % (addr, port))
	self.socket.shutdown(socket.SHUT_RDWR)
	self.socket.close()

    def receive(self):
	data, addr = self.socket.recvfrom(8192)
	if not data:
	    raise socket.error("UDP socket closed on port " + self.port)
	return data, addr

    def send(self, data, addr):
	(host, port) = addr
	nerve.log("SEND -> " + str(host) + ":" + str(port) + ": " + data)
	self.socket.sendto(data + '\n', addr)

    def run(self):
	nerve.log("Starting UDP Server")
	while True:
	    self.open()

	    while True:
		try:
		    data, addr = self.receive()
		    data = data.strip('\n')
		    (host, port) = addr
		    if (data):
			nerve.log("RECV <- " + str(host) + ":" + str(port) + ": " + data)
			msg = nerve.Message(data, UDPNetworkPortal(self, addr), self)
			nerve.dispatch(msg)

		except socket.error, e:
		    nerve.log("Socket Error: " + str(e))
		    break

		except:
		    nerve.log(traceback.format_exc())

	    self.close()
	    time.sleep(1)

 
