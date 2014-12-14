#!/usr/bin/python
# -*- coding: utf-8 -*-


class InvalidRequest (Exception):
    pass


class Portal (object):
    def __init__(self):
	pass

    def send(self, text):
	raise Exception("Error: send() function is not defined on this portal")


class CallbackPortal (Portal):
    def __init__(self, func):
	self.callback = func

    def send(self, msg):
	return self.callback(msg)


class Message (object):
    def __init__(self, line, from_port, to_port):
	self.from_port = from_port
	self.to_port = to_port
	self.line = line
	self.args = line.split()
	self.query = self.args.pop(0)
	self.names = self.query.split('.')

    def reply(self, line):
	self.from_port.send(line)

    def device_name(self):
	return '.'.join(self.names[:-1])

    def checkargs(self, min, max=None):
	length = len(self.args)
	if max is None:
	    if length == min:
		return True
	    return False
	else:
	    if length >= min and length <= max:
		return True
	    return False


class Device (object):
    def __init__(self):
	self.name = None
	self.parent = None
	self.subdevices = { }

    def device_name(self):
	if self.name is None:
	    return '(root)'
	name = self.name
	parent = self.parent
	while parent is not None and parent.name is not None:
	    name = parent.name + '.' + name
	    parent = parent.parent
	return name

    def add(self, name, dev, *args):
	names = name.split('.', 1)
	if len(names) > 1:
	    if names[0] not in self.subdevices:
		self.subdevices[names[0]] = Device()
	    subdev = self.subdevices[names[0]]
	    return subdev.add(names[1], dev)

	else:
	    self.subdevices[names[0]] = dev
	    dev.name = names[0]
	    dev.parent = self
	    return dev

    def get(self, name):
	devname, sep, rest = name.partition('.')
	# we want to make sure we don't get internal python objects accidentally
	if devname.startswith('__'):
	    return None

	if devname in self.subdevices:
	    if rest:
		return self.subdevices[name].get(rest)
	    else:
		return self.subdevices[name]
	return None

    def get_local(self, name):
	if name in self.subdevices:
	    return self.subdevices[name]
	return None

    def query(self, line, from_port=None, to_port=None):
	msg = Message(line, from_port, to_port)
	self.dispatch(msg)

    def dispatch(self, msg, index=0):
	if index + 1 >= len(msg.names):
	    func = getattr(self, msg.names[index])
	    #func = getattr(self, 'query_' + msg.names[index])
	    return func(msg)
	else:
	    dev = self.get_local(msg.names[index])
	    if dev is None:
		raise InvalidRequest("No subdevice named " + msg.names[index] + " in device " + self.device_name())
	    return dev.dispatch(msg, index + 1)

import Queue
import time

class Something (object):
    dispatch_queue = Queue.PriorityQueue()

    @staticmethod
    #def request(url, *args, delay=0, callback=None):
    def request(url, args, delay=0, callback=None):
	entry = (time.time() + delay, url, args, callback)
	Something.dispatch_queue.put(entry)


    def dispatch_request(self, url, args):
	urldata = urlparse.urlparse(url)
	# TODO do all the rest

    def run(self):
	while not self.thread.stopflag.wait(1):
	    try:
		entry = Something.dispatch_queue.get(True, 1.0)

		## If the next entry is scheduled for the future, then put it back and wait a bit
		if time.time() > entry[0]:
		    Something.dispatch_queue.put(entry)
		    time.sleep(0.1)

		## Otherwise, disptach the request
		else:
		    result = self.disptach_request(entry[1], entry[2])
		    if entry[3] is not None:
			entry[3](result)

		Something.dispatch_queue.task_done()
	    except queue.Empty as e:
		pass

class AliasDevice (Device):
    def __init__(self, portal, uri):
	pass

    def dispatch(self, msg, index=0):
	pass

