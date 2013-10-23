
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
	Console.log("SEND -> " + str(host) + ":" + str(port) + ": " + data)
	self.socket.sendto(data + '\n', addr)

    def do_thread(self):
	while 1:
	    self.open()
	    while 1:
		try:
		    data, addr = self.recv()
		    data = data.strip('\n')
		    (host, port) = addr
		    Console.log("RECV <- " + str(host) + ":" + str(port) + ": " + data)
		    if (data):
			msg = Message(data, addr, self)
			Namespace.root.dispatch(msg)
		except socket.error, e:
		    Console.log("Socket Error: " + str(e))
		    break
		except:
		    t = traceback.format_exc()
		    Console.log(t)
	    self.close()


class Device (object):
    def __init__(self):
	self.name = None

class Namespace (object):
    root = None

    def __init__(self):
	self.devices = { }

    def add(self, name, dev):
	self.devices[name] = dev
	dev.name = name

    def get(self, name):
	if name in self.devices:
	    return self.devices[name]
	return None

    def query(self, line, addr=None, server=None):
	msg = Message(line, addr, server)
	self.dispatch(msg)

    def dispatch(self, msg):
	# TODO test for key error
	if len(msg.names) != 2:
	    return
	dev = self.devices[msg.names[0]]
	func = getattr(dev, msg.names[1])
	return func(msg)

	#obj = self.devices
	#for i in range(0, len(msg.names)):
	#    sub = obj[msg.names[i]]
	#    if isinstance(sub, Namespace):
	#	if i == len(msg.names) - 1:
	#	    raise InvalidRequest()
	#	obj = sub.devices
	#    elif isinstance(sub, types.MethodType):
	#	return sub(self, msg)



class Console (object):
    @staticmethod
    def log(text):
	print time.strftime("%Y-%m-%d %H:%M") + " " + text

    @staticmethod
    def loop():
        while 1:
	    line = raw_input(">> ")
	    if line == 'quit':
		break


Namespace.root = Namespace();

def add_device(name, device):
    Namespace.root.add(name, device)

def get_device(name):
    return Namespace.root.get(name)

def query(line, addr=None, server=None):
    Namespace.root.query(line, addr, server)

def loop():
    Console.loop()

