#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

import nerve.serial

class DeskClock (nerve.serial.SerialDevice):
    def __init__(self, **config):
        nerve.serial.SerialDevice.__init__(self, **config)
        self.relay1 = False

    def p0(self):
        if len(msg.args):
            self.send('P0=' + str(int(msg.args[0], 16)) + '\n')

    def p1(self):
        if len(msg.args):
            self.send('P1=' + str(int(msg.args[0], 16)) + '\n')

    def relay_toggle(self):
        self.relay1 = not self.relay1
        if self.relay1:
            self.send('R1=1\n')
        else:
            self.send('R1=0\n')

    def do_idle(self):
        self.send('L0=' + time.strftime("%H:%M %a %b %d") + '\n')

        player = nerve.get_object("/devices/player")
        if player != None:
            title = player.title.ljust(16)
            title = title[0:16]
            self.send('L1=' + title + '\n')
        else:
            self.send('L1=                \n')

    def do_receive(self, line):
        #print line
        if line == "B7=0" or line == 'I0=A2C8':
            nerve.query("/devices/player/next")
        elif line == "B6=0" or line == 'I0=A2A8':
            nerve.query("/devices/player/toggle")
        elif line == "B5=0" or line == 'I0=A298':
            nerve.query("/devices/player/previous")
        elif line == "B4=0":
            rgb = nerve.get_object("/devices/rgb")
            rgb.send('key 248')
        elif line == "B3=0" or line == 'I0=A207':
            self.relay_toggle()
            #self.relay_toggle(msg)
        elif line == "B0=0":
            nerve.query("/devices/player/shuffle")
        elif line == "B1=0":
            nerve.query("/devices/player/sort")
        elif line[0:5] == 'I0=A2':
            rgb = nerve.get_object("/devices/rgb")
            rgb.send('key 2' + line[5:7])

nerve.set_object('/devices/deskclock', DeskClock(file="/dev/ttyACM0", baud=19200))


