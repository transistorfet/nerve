#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import sys
import serial
import thread
import select
import traceback

class SerialDevice (nerve.Device):
    def __init__(self, file, baud):
	nerve.Device.__init__(self)

	self.file = file
	self.baud = baud
	self.serial = serial.Serial(file, baud)

	if sys.platform == 'win32':
	    self.thread = nerve.Task('SerialTask', self.run_win32)
	    self.thread.daemon = True
	else:
	    self.thread = nerve.Task('SerialTask', self.run_posix)
	self.thread.start()

    def send(self, data):
	nerve.log("SEND -> " + str(self.file) + ": " + data)
	self.serial.write(data + '\n')

    def do_receive(self, msg):
	pass

    def do_idle(self):
	pass

    def run_posix(self):
	while not self.thread.stopflag.isSet():
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
	while not self.thread.stopflag.isSet():
	    try:
		line = self.serial.readline()
		line = line.strip()
		nerve.log("RECV <- " + self.file + ": " + line)
		self.do_receive(line)

	    except:
		nerve.log(traceback.format_exc())


class NerveSerialDevice (SerialDevice):
    def dispatch(self, msg, index=0):
	if index + 1 != len(msg.names):
	    raise nerve.InvalidRequest

	# TODO This is here temporarily to allow for overriding functions
	if hasattr(self, msg.names[index]):
	    func = getattr(self, msg.names[index])
	    return func(self, msg)

	query = '.'.join(msg.names[index:])
	if len(msg.args):
	    query += ' ' + ' '.join(msg.args)
	self.reply = msg.from_port
	self.send(query)

    def do_receive(self, line):
	if self.reply:
	    self.reply.send(self.name + '.' + line)


