#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import os


class OnkyoStereo (nerve.Device):
    def __init__(self, serial, **config):
        nerve.Device.__init__(self, **config)
        self.serial = serial

    def power(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x4B36D32C)

    def volup(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x4BB640BF)
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x4BB640BF)

    def voldown(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x4BB6C03F)
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x4BB6C03F)

    def mute(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x4BB6A05F)

    def tape(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x4BB610EF)

    def tuner(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x4BB6D02F)

    def speaker_ab(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x4B3611EE)


# 1 - 0x010
# 2 - 0x810
# 3 - 0x410
# 4 - 0xC10
# 5 - 0x210
# 6 - 0xA10
# 7 - 0x610
# 8 - 0xE10
# 9 - 0x110
# 0 - 0x910
class SonyTelevision (nerve.Device):
    def __init__(self, serial, **config):
        nerve.Device.__init__(self, **config)
        self.serial = serial

    def power(self):
        self.serial.send("ir S 0xA90")

    def volup(self):
        self.serial.send("ir S 0x490")

    def voldown(self):
        self.serial.send("ir S 0xC90")

    def mute(self):
        self.serial.send("ir S 0x290")

    def input(self):
        self.serial.send("ir S 0xA50")

    def ps3(self):
        self.serial.send("ir S 0xA50")
        self.serial.send("ir S 0x010")

    def netbook(self):
        self.serial.send("ir S 0xA50")
        self.serial.send("ir S 0x810")

    def computer(self):
        self.serial.send("ir S 0xA50")
        self.serial.send("ir S 0x410")

    def appletv(self):
        self.serial.send("ir S 0xA50")
        self.serial.send("ir S 0xC10")



class HDMISelector (nerve.Device):
    def __init__(self, serial, **config):
        nerve.Device.__init__(self, **config)
        self.serial = serial

    def s1(self):
        self.serial.send("ir N 0x1FE58A7")

    def s2(self):
        self.serial.send("ir N 0x1FE20DF")

    def s3(self):
        self.serial.send("ir N 0x1FE609F")




class SonyStereo (nerve.Device):
    def __init__(self, serial, **config):
        nerve.Device.__init__(self, **config)
        self.serial = serial

    def power(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0xA81)

    def volup(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x481)
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x481)

    def voldown(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0xC81)
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0xC81)

    def mute(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x281)

    def tape(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0xC41)

    def tuner(self):
        nerve.query("/devices/mysensors/11/1/send_msg", 32, 0x841)


class PanasonicTelevision (nerve.Device):
    def __init__(self, serial, **config):
        nerve.Device.__init__(self, **config)
        self.serial = serial

    def power(self):
        self.serial.send("ir P 0x4004 0x100BCBD")

    def volup(self):
        self.serial.send("ir P 0x4004 0x1000405")

    def voldown(self):
        self.serial.send("ir P 0x4004 0x1008485")

    def mute(self):
        self.serial.send("ir P 0x4004 0x1004C4D")

    def ps3(self):
        self.serial.send("ir P 0x4004 0x100A0A1")
        self.serial.send("ir P 0x4004 0x1008889")

    def netbook(self):
        self.serial.send("ir P 0x4004 0x100A0A1")
        self.serial.send("ir P 0x4004 0x1004849")

    def computer(self):
        self.serial.send("ir P 0x4004 0x100A0A1")
        self.serial.send("ir P 0x4004 0x1004849")

    def appletv(self):
        self.serial.send("ir P 0x4004 0x100A0A1")
        self.serial.send("ir P 0x4004 0x100C8C9")


rgb = nerve.get_object('/devices/rgb')
nerve.set_object('/devices/stereo', OnkyoStereo(rgb))
nerve.set_object('/devices/tv', SonyTelevision(rgb))
nerve.set_object('/devices/hdmi', HDMISelector(rgb))


