#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve
import os

class Stereo (nerve.Device):
    def __init__(self, serial, **config):
        nerve.Device.__init__(self, **config)
        self.serial = serial

    def power(self):
        self.serial.send("ir S A81")

    def volup(self):
        self.serial.send("ir S 481")

    def voldown(self):
        self.serial.send("ir S C81")

    def tape(self):
        self.serial.send("ir S C41")

    def tuner(self):
        self.serial.send("ir S 841")


class Television (nerve.Device):
    def __init__(self, serial, **config):
        nerve.Device.__init__(self, **config)
        self.serial = serial

    def power(self):
        self.serial.send("ir P 4004 100BCBD")

    def volup(self):
        self.serial.send("ir P 4004 1000405")

    def voldown(self):
        self.serial.send("ir P 4004 1008485")

    def ps3(self):
        self.serial.send("ir P 4004 100A0A1")
        self.serial.send("ir P 4004 1008889")

    def netbook(self):
        self.serial.send("ir P 4004 100A0A1")
        self.serial.send("ir P 4004 1004849")

    def computer(self):
        self.serial.send("ir P 4004 100A0A1")
        self.serial.send("ir P 4004 1004849")


#nerve.add_portal('raw.UDPServer', 5959)

#rgb = nerve.add_device('rgb', 'serial.NerveSerialDevice', '/dev/ttyACM0', 19200)
rgb = nerve.get_object('devices/rgb')
nerve.set_object('devices/stereo', Stereo(rgb))
nerve.set_object('devices/tv', Television(rgb))

#nerve.add_device("sys", Sys())
#nerve.add_device("player", 'vlc.VLCHTTP')

#nerve.add_device('medialib', 'medialib.MediaLib')

#nerve.add_portal('http.HTTPServer', 8888)

#nerve.add_portal('raw.Console')

