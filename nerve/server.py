
import nerve

import socket
import thread
import sys
import os
import traceback
import string

class NetworkNode (nerve.Node):
    def __init__(self, server, addr):
	self.server = server
	self.addr = addr

    def send(self, text):
	self.server.send(text, self.addr)


class Server (object):
    def __init__(self, port):
	self.port = port
	thread.start_new_thread(self.do_thread, ())

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
	(host, port) = addr
	nerve.Console.log("SEND -> " + str(host) + ":" + str(port) + ": " + data)
	self.socket.sendto(data + '\n', addr)

    def do_thread(self):
	while 1:
	    self.open()
	    while 1:
		try:
		    data, addr = self.recv()
		    data = data.strip('\n')
		    (host, port) = addr
		    nerve.Console.log("RECV <- " + str(host) + ":" + str(port) + ": " + data)
		    if (data):
			msg = nerve.Message(data, NetworkNode(self, addr), self)
			nerve.dispatch(msg)
		except socket.error, e:
		    nerve.Console.log("Socket Error: " + str(e))
		    break
		except:
		    t = traceback.format_exc()
		    nerve.Console.log(t)
	    self.close()

 
