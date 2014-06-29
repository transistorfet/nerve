#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from nerve.serial import SerialDevice

class DeskClock (SerialDevice):
    def __init__(self, file, baud):
	SerialDevice.__init__(self, file, baud)
	self.relay1 = False

    def p0(self, msg):
	if len(msg.args):
	    self.serial.write('P0=' + str(int(msg.args[0], 16)) + '\n')

    def p1(self, msg):
	if len(msg.args):
	    self.serial.write('P1=' + str(int(msg.args[0], 16)) + '\n')

    def relay_toggle(self, msg):
	self.relay1 = not self.relay1
	if self.relay1:
	    self.serial.write('R1=1\n')
	else:
	    self.serial.write('R1=0\n')

    def do_idle(self):
	self.serial.write('L0=' + time.strftime("%H:%M %a %b %d") + '\n')

	music = nerve.get_device("music")
	if music != None:
	    title = music.title.ljust(16)
	    title = title[0:16]
	    self.serial.write('L1=' + title.encode('ascii', 'replace') + '\n')
	else:
	    self.serial.write('L1=                \n')

    def do_receive(self, line):
	#print line
	if line == "B7=0" or line == 'I0=A2C8':
	    nerve.query("music.next")
	elif line == "B6=0" or line == 'I0=A2A8':
	    nerve.query("music.toggle")
	elif line == "B5=0" or line == 'I0=A298':
	    nerve.query("music.previous")
	elif line == "B4=0":
	    rgb = nerve.get_device("rgb")
	    rgb.send('key 248')
	elif line == "B3=0" or line == 'I0=A207':
	    nerve.query(self.name + ".relay_toggle")
	    #self.relay_toggle(msg)
	elif line == "B0=0":
	    nerve.query("music.shuffle")
	elif line == "B1=0":
	    nerve.query("music.sort")
	elif line[0:5] == 'I0=A2':
	    rgb = nerve.get_device("rgb")
	    rgb.send('key 2' + line[5:7])

#from config.panther.devices.deskclock import DeskClock

nerve.add_portal('raw.UDPServer', 5959)
#nerve.add_portal('raw.TCPServer', 5959)

nerve.add_device('deskclock', DeskClock("/dev/ttyACM0", 19200))
rgb = nerve.add_device('rgb', 'serial.NerveSerialDevice', "/dev/ttyACM1", 19200)

nerve.add_device('music', 'xmms2.Xmms2')

nerve.add_portal('raw.Console')


