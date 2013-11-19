
import nerve

import sys
import serial
import thread
import select
import traceback

class SerialDevice (nerve.Device):
    def __init__(self, file, baud):
	self.file = file
	nerve.Device.__init__(self)
	self.baud = baud
	self.serial = serial.Serial(file, baud)
	if sys.platform == 'win32':
	    thread.start_new_thread(self.do_win32_thread, ())
	else:
	    thread.start_new_thread(self.do_thread, ())

    def send(self, data):
	nerve.Console.log("SEND -> " + str(self.file) + ": " + data)
	self.serial.write(data + '\n')

    def do_receive(self, msg):
	pass

    def do_idle(self):
	pass

    def do_thread(self):
	while 1:
	    try:
		self.do_idle()
		(rl, wl, el) = select.select([ self.serial ], [ ], [ ], 0.1)
		if rl and self.serial in rl:
		    line = self.serial.readline()
		    line = line.strip()
		    nerve.Console.log("RECV <- " + self.file + ": " + line)
		    self.do_receive(line)
	    except:
		t = traceback.format_exc()
		nerve.Console.log(t)

    def do_win32_thread(self):
	while 1:
	    try:
		line = self.serial.readline()
		line = line.strip()
		nerve.Console.log("RECV <- " + self.file + ": " + line)
		self.do_receive(line)
	    except:
		t = traceback.format_exc()
		nerve.Console.log(t)


class NerveSerialDevice (SerialDevice):
    def dispatch(self, msg, index=0):
	if index + 1 != len(msg.names):
	    raise InvalidRequest
	query = '.'.join(msg.names[index:])
	if len(msg.args):
	    query += ' ' + ' '.join(msg.args)
	self.reply = msg.from_node
	self.send(query)

    def do_receive(self, line):
	if self.reply:
	    self.reply.send(self.name + '.' + line)


