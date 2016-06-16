#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

import nerve.serial

class DeskClock (nerve.serial.SerialDevice):
    def __init__(self, **config):
        nerve.serial.SerialDevice.__init__(self, **config)
        self.relay1 = False

    def p0(self, value):
        self.send('P0=' + str(int(value, 16)) + '\n')

    def p1(self, value):
        self.send('P1=' + str(int(value, 16)) + '\n')

    def relay_toggle(self):
        self.relay1 = not self.relay1
        if self.relay1:
            self.send('R1=1\n')
        else:
            self.send('R1=0\n')

    def on_idle(self):
        self.send('L0=' + time.strftime("%H:%M %a %b %d") + '\n')

        player = nerve.get_object("/devices/player")
        if player != None:
            player.getsong()
            title = player.title.ljust(16)
            title = title[0:16]
            self.send('L1=' + title + '\n')
        else:
            self.send('L1=                \n')

    def on_receive(self, line):
        #print line
        if line == "B7=0" or line == 'I0=N:A25DC837':
            nerve.query("/devices/player/next")
        elif line == "B6=0" or line == 'I0=N:A25DA857':
            nerve.query("/devices/player/toggle")
        elif line == "B5=0" or line == 'I0=N:A25D9867':
            nerve.query("/devices/player/previous")
        elif line == "B4=0":
            nerve.query("/devices/rgb/key", "0x248")
        elif line == "B3=0" or line == 'I0=N:A25D07F8':
            self.relay_toggle()
        elif line == "B0=0":
            nerve.query("/devices/player/shuffle")
        elif line == "B1=0":
            nerve.query("/devices/player/sort")
        elif line.startswith('I0=N:A25D'):
            nerve.query("/devices/rgb/key", "0x2" + line[9:11])

nerve.set_object('/devices/deskclock', DeskClock(file="/dev/ttyACM0", baud=19200))


