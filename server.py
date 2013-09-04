
import socket
import thread
import time
import sys
import os
import traceback
import string

class InvalidRequest (Exception):
    pass

class Message (object):
    def __init__(self, line, addr, server):
	self.addr = addr
	self.server = server
	self.line = line
	self.args = line.split()
	self.query = self.args.pop(0)
	self.names = self.query.split('.')

class Server (object):
    def __init__(self, port, handler):
	self.handler = handler
	self.port = port
	thread.start_new_thread(self.do_thread, (self,))

    def open(self):
	self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	self.socket.bind(('', self.port))

    def close(self):
	self.socket.close()

    def recv(self):
	data, addr = self.socket.recvfrom(8192)
	if not data:
	    raise socket.error("closed")
	return data, addr

    def send(self, data, addr):
	self.socket.sendto(data, addr)

    def do_thread(self, nothing):
	while 1:
	    self.open()
	    while 1:
		try:
		    data, addr = self.recv()
		    data = data.strip('\n')
		    (host, port) = addr
		    print "RECV from " + str(host) + ":" + str(port) + ": " + data
		    msg = Message(data, addr, self)
		    self.handler(msg)
		except socket.error, e:
		    print "Socket Error: " + str(e)
		    break
		except:
		    t = traceback.format_exc()
		    print t
	    self.close()


