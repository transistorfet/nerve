#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import socket
import thread
import sys
import os
import traceback
import string


class TCPClient (nerve.Portal):
    def __init__(self, addr=None):
	self.socket = None
	self.buffer = ""

	if addr:
	    self.connect(addr)

    def connect(self, addr):
	if self.socket is not None:
	    self.close()

	self.host, self.port = addr
	for res in socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM):
	    af, socktype, proto, canonname, sa = res
	    try:
		self.socket = socket.socket(af, socktype, proto)
	    except socket.error as msg:
		self.socket = None
		continue

	    try:
		self.socket.connect(sa)
	    except socket.error as msg:
		self.socket.close()
		self.socket = None
		continue
	    break
	if self.socket is None:
	    return False
	return True

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
		self.socket = None
		raise socket.error("TCP socket closed by remote end. (" + str(self.host) + ":" + str(self.port) + ")")
	    self.buffer = self.buffer + data

    def send(self, data):
	nerve.log("SEND -> " + str(self.host) + ":" + str(self.port) + ": " + data)
	self.socket.send(data + '\n')

    def close(self):
	if self.socket:
	    self.socket.close()
	    self.socket = None

    def start_thread(self):
	thread.start_new_thread(self.do_connection_thread, ())

    def do_connection_thread(self):
	while 1:
	    try:
		data = self.readline()
		data = data.strip('\n')
		if (data):
		    nerve.log("RECV <- " + str(self.host) + ":" + str(self.port) + ": " + data)
		    msg = nerve.Message(data, self, self.server)
		    nerve.dispatch(msg)

	    except socket.error, e:
		nerve.log("Socket Error: " + str(e))
		break

	    except:
		nerve.log(traceback.format_exc())
	self.close()


