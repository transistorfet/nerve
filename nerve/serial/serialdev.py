#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import sys
import serial
import thread
import threading
import select
import traceback

class SerialDevice (nerve.Device):
    def __init__(self, **config):
	nerve.Device.__init__(self, **config)

	self.file = config['file']
	self.baud = config['baud']
	self.serial = serial.Serial(self.file, self.baud)

	if sys.platform == 'win32':
	    self.thread = nerve.Task('SerialTask', self.run_win32)
	    self.thread.daemon = True
	else:
	    self.thread = nerve.Task('SerialTask', self.run_posix)
	self.thread.start()

    @staticmethod
    def get_defaults():
	defaults = nerve.Device.get_defaults()
	defaults['file'] = ''
	defaults['baud'] = 19200
	return defaults

    def send(self, data):
	nerve.log("SEND -> " + str(self.file) + ": " + data)
	self.serial.write(data + '\n')

    def do_receive(self, line):
	pass

    def do_idle(self):
	pass

    def run_posix(self):
	while not self.thread.stopflag.is_set():
	    try:
		self.do_idle()
		(rl, wl, el) = select.select([ self.serial ], [ ], [ ], 0.1)
		if rl and self.serial in rl:
		    line = self.serial.readline()
		    line = line.strip()
		    nerve.log("RECV <- " + self.file + ": " + line)
		    self.do_receive(line)

	    except:
		nerve.log(traceback.format_exc())

    def run_win32(self):
	while not self.thread.stopflag.is_set():
	    try:
		line = self.serial.readline()
		line = line.strip()
		nerve.log("RECV <- " + self.file + ": " + line)
		self.do_receive(line)

	    except:
		nerve.log(traceback.format_exc())


class NerveSerialDevice (SerialDevice):
    def __init__(self, **config):
	SerialDevice.__init__(self, **config)
	self.received = threading.Event()
	self.data = None

    def __getattr__(self, name):
	def serial_getter(*args, **kwargs):
	    querystr = name
	    if len(args) > 0:
		query_string += ' ' + ' '.join(args)
	    self.received.clear()
	    self.send(querystr)
	    if self.received.wait(2) is True:
		result = self.data
		self.data = None
		self.received.clear()
		return result
	    return None
	return serial_getter

    def do_receive(self, line):
	(ref, _, args) = line.partition(" ")
	self.data = args
	self.received.set()

