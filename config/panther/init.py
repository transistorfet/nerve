#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import os

class Stereo (nerve.Device):
    def __init__(self, serial, **config):
        nerve.Device.__init__(self, **config)
        self.serial = serial

    def power(self):
        #self.serial.send("ir S 0xA81")
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0xA81)

    def volup(self):
        #self.serial.send("ir S 0x481")
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x481)
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x481)

    def voldown(self):
        #self.serial.send("ir S 0xC81")
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0xC81)
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0xC81)

    def tape(self):
        #self.serial.send("ir S 0xC41")
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0xC41)

    def tuner(self):
        #self.serial.send("ir S 0x841")
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x841)


class Television (nerve.Device):
    def __init__(self, serial, **config):
        nerve.Device.__init__(self, **config)
        self.serial = serial

    def power(self):
        self.serial.send("ir P 0x4004 0x100BCBD")

    def volup(self):
        self.serial.send("ir P 0x4004 0x1000405")

    def voldown(self):
        self.serial.send("ir P 0x4004 0x1008485")

    def ps3(self):
        self.serial.send("ir P 0x4004 0x100A0A1")
        self.serial.send("ir P 0x4004 0x1008889")

    def netbook(self):
        self.serial.send("ir P 0x4004 0x100A0A1")
        self.serial.send("ir P 0x4004 0x1004849")

    def computer(self):
        self.serial.send("ir P 0x4004 0x100A0A1")
        self.serial.send("ir P 0x4004 0x1004849")


rgb = nerve.get_object('/devices/rgb')
nerve.set_object('/devices/stereo', Stereo(rgb))
nerve.set_object('/devices/tv', Television(rgb))


