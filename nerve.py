
import socket
import thread
import time
import sys
import os
import traceback
import string

class InvalidRequest (Exception):
    pass

# TODO change Node to Endpoint or something

class Node (object):
    def __init__(self):
	pass

    def send(self, text):
	# TODO emit error??
	pass

class NetworkNode (Node):
    def __init__(self, server, addr):
	self.server = server
	self.addr = addr

    def send(self, text):
	self.server.send(text, self.addr)


class Message (object):
    # TODO addr and server could be replaced with a node, and then all the code will use node.send(text) to reply to the sender
    def __init__(self, line, from_node, to_node):
	self.from_node = from_node
	self.to_node = to_node
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
			msg = Message(data, NetworkNode(self, addr), self)
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

    def dispatch(self, msg, index=0):
	if index + 1 != len(msg.names):
	    raise InvalidRequest
	func = getattr(self, msg.names[index])
	return func(msg)


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

    def query(self, line, from_node=None, to_node=None):
	msg = Message(line, from_node, to_node)
	self.dispatch(msg)

    def dispatch(self, msg, index=0):
	if index > len(msg.names):
	    raise InvalidRequest
	if not msg.names[index] in self.devices:
	    raise InvalidRequest
	dev = self.devices[msg.names[index]]
	return dev.dispatch(msg, index + 1)


class Console (Node):
    def send(self, text):
	# TODO this is how a response is sent to the console??
	print text

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


