#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

class Stereo (nerve.Device):
    def __init__(self, serial):
	nerve.Device.__init__(self)
	self.serial = serial

    def power(self, msg):
	self.serial.send("ir S A81")

    def volup(self, msg):
	self.serial.send("ir S 481")

    def voldown(self, msg):
	self.serial.send("ir S C81")

    def tape(self, msg):
	self.serial.send("ir S C41")

    def tuner(self, msg):
	self.serial.send("ir S 841")


class Television (nerve.Device):
    def __init__(self, serial):
	nerve.Device.__init__(self)
	self.serial = serial

    def power(self, msg):
	self.serial.send("ir P 4004 100BCBD")

    def volup(self, msg):
	self.serial.send("ir P 4004 1000405")

    def voldown(self, msg):
	self.serial.send("ir P 4004 1008485")

    def ps3(self, msg):
	self.serial.send("ir P 4004 100A0A1")
	self.serial.send("ir P 4004 1008889")

    def netbook(self, msg):
	self.serial.send("ir P 4004 100A0A1")
	self.serial.send("ir P 4004 1004849")


nerve.add_portal('udpserver.UDPServer', 5959)

#from nerve.portals.udpserver import UDPServer
#serv = UDPServer(5959)

#from nerve.devices.serialdev import NerveSerialDevice
#rgb = nerve.add_device("rgb", NerveSerialDevice("COM9", 19200))
rgb = nerve.add_device('rgb', 'serialdev.NerveSerialDevice', 'COM9', 19200)

"""
def red(self, msg):
    if len(msg.args):
	self._redval = msg.args[0]
	self.send("color %02x%02x%02x" % (int(self._redval, 16), int(self._greenval, 16), int(self._blueval, 16)))
    else:
	msg.reply(msg.query + " " + self._redval)

def green(self, msg):
    if len(msg.args):
	self._greenval = msg.args[0]
	self.send("color %02x%02x%02x" % (int(self._redval, 16), int(self._greenval, 16), int(self._blueval, 16)))
    else:
	msg.reply(msg.query + " " + self._greenval)

def blue(self, msg):
    if len(msg.args):
	self._blueval = msg.args[0]
	self.send("color %02x%02x%02x" % (int(self._redval, 16), int(self._greenval, 16), int(self._blueval, 16)))
    else:
	msg.reply(msg.query + " " + self._blueval)

rgb._redval = 'ff'
rgb._greenval = 'ff'
rgb._blueval = 'ff'

rgb.red = red
rgb.green = green
rgb.blue = blue
"""

nerve.add_device("stereo", Stereo(rgb))
nerve.add_device("tv", Television(rgb))

#from nerve.devices.win32sys import Win32Sys
#nerve.add_device("sys", Win32Sys())
nerve.add_device("sys", 'win32sys.Win32Sys')
#from nerve.devices.vlchttp import VLCHTTP
#nerve.add_device("music", VLCHTTP())
nerve.add_device("music", 'vlchttp.VLCHTTP')

#from nerve.devices.layout import LayoutDevice
#nerve.add_device('layout', LayoutDevice())
nerve.add_device('layout', 'layout.LayoutDevice')

#from nerve.portals.httpserver import HTTPServer
#HTTPServer(8999)
nerve.add_portal('httpserver.HTTPServer', 8999)

#from nerve.portals.console import Console
#Console()
nerve.add_portal('console.Console')

#nerve.loop()
 
"""
def dispatch(data, addr):
    (host, port) = addr
    msg = data.lower().strip('\n')
    print "RECV from " + str(host) + ":" + str(port) + ": " + msg

    words = msg.split()
    cmd = words[0].split('.')
    if cmd[0] == 'music':
	if cmd[1] == 'next':
	    music.next()
	elif cmd[1] == 'previous':
	    music.previous()
	elif cmd[1] == 'toggle':
	    s = music.getPlaybackStatus()
	    if s == winamp.Winamp.PLAYBACK_PLAYING or s == winamp.Winamp.PLAYBACK_PAUSE:
		music.pause()
	    elif s == winamp.Winamp.PLAYBACK_NOT_PLAYING:
		music.play()
	elif cmd[1] == 'getvolume':
	    volume = music.getVolume()
	    serv.send(str(volume), addr)
	elif cmd[1] == 'getsong':
	    song = music.getCurrentPlayingTitle()
	    serv.send(song, addr)
    elif cmd[0] == 'stereo':
	if cmd[1] == 'power':
	    arduino.write("CA\n")
	elif cmd[1] == 'volup':
	    arduino.write("CB\n")
	elif cmd[1] == 'voldown':
	    arduino.write("CC\n")
	elif cmd[1] == 'tape':
	    arduino.write("CD\n")
	elif cmd[1] == 'tuner':
	    arduino.write("CE\n")
    elif cmd[0] == 'tv':
	if cmd[1] == 'power':
	    arduino.write("Ca\n")
	elif cmd[1] == 'volup':
	    arduino.write("Cb\n")
	elif cmd[1] == 'voldown':
	    arduino.write("Cc\n")
	elif cmd[1] == 'ps3':
	    arduino.write("Cd\n")
	    arduino.write("Ce\n")
	elif cmd[1] == 'netbook':
	    arduino.write("Cd\n")
	    arduino.write("Cf\n")
"""


