#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import unicodedata

import nerve.serial
import nerve.events

class DeskClock (nerve.serial.SerialDevice):
    def __init__(self, **config):
        nerve.serial.SerialDevice.__init__(self, **config)
        self.relay1 = False
        self.temp = 0.0

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

    def t0(self):
        #self.send('T0\n')
        return self.temp

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
            #self.relay_toggle()
            nerve.query("http://panther:8888/devices/mysensors/12/3/toggle")
        elif line == "B2=0":
            nerve.events.publish(self.get_pathname() + '/B2', name='B2', value=True)
        elif line == "B1=0":
            nerve.query("/devices/player/sort")
        elif line == "B0=0":
            nerve.query("/devices/player/shuffle")
        elif line.startswith('I0=N:A25D'):
            nerve.query("/devices/rgb/key", "0x2" + line[9:11])
            nerve.events.publish(self.get_pathname() + '/ir', name='ir', value=line[3:])
        elif line.startswith('T0='):
            self.temp = float(line[3:])
            nerve.log('deskclock: ' + str(self.temp) + 'C', logtype='info')
            nerve.events.publish(self.get_pathname() + '/t0', name='t0', value=self.temp)

#nerve.set_object('/devices/deskclock', DeskClock(file="/dev/ttyACM0", baud=115200))



class DeskClock2 (nerve.serial.SerialDevice):
    def __init__(self, **config):
        nerve.serial.SerialDevice.__init__(self, **config)
        self.idle_count = 0
        self.temp = 0.0
        self.outdoor_temp = 0.0
        self.last_lines = ["" for _ in range(5) ]

        nerve.events.subscribe('devices/deskclock/t0', action=self._update_temp)

    def p0(self, value):
        self.send('P0=' + str(int(value, 16)) + '\n')

    def p1(self, value):
        self.send('P1=' + str(int(value, 16)) + '\n')

    def t0(self):
        #self.send('T0\n')
        return self.temp

    def _update_temp(self, event):
        self.temp = event['value']

    def update_outdoor_temp(self, value):
        self.outdoor_temp = float(value)

    def on_idle(self):
        #text_limit = 22; # for 12pt font
        text_limit = 19;

        date = time.strftime("%H:%M %a %b %d")
        temp = "{:.1f}C".format(self.temp).rjust(text_limit)
        outdoor_temp = "{:.1f}C".format(self.outdoor_temp).rjust(text_limit)

        player = nerve.get_object("/devices/player")
        if player != None:
            player.getsong()
            artist = normalize(player.artist[:text_limit - 1])
            title = normalize(player.title[:text_limit - 1])

            lines = [
                "\x1b[2m{}".format(date),
                "\x1b[3m{}".format(artist),
                "\x1b[5m{}".format(title),
                "\x1b[9m{}".format(temp),
                "\x1b[1m{}".format(outdoor_temp),
            ]

            for (i, (newline, oldline)) in enumerate(zip(lines, self.last_lines)):
                if newline != oldline:
                    self.send("L{}={}".format(i, newline))
            self.last_lines = lines

            #msg = 'L0=\x1b[2m{}\r\x1b[3m{}\r\x1b[5m{}\r\x1b[9m{}\r\x1b[1m{}'.format(date, artist, title, temp, outdoor_temp)
            #if msg != self.last_msg:
            #    self.send(msg)
            #    self.last_msg = msg
        else:
            #self.send('L1=' + (' ' * 32) + '\n')
            #self.send('L2=' + (' ' * 32) + '\n')
            pass

    def on_receive(self, line):
        #print line
        if line == "B7=1" or line == 'I0=N:A25DC837':
            nerve.query("/devices/player/next")
        elif line == "B6=1" or line == 'I0=N:A25DA857':
            nerve.query("/devices/player/toggle")
        elif line == "B5=1" or line == 'I0=N:A25D9867':
            nerve.query("/devices/player/previous")
        elif line == "B4=1":
            nerve.query("/devices/rgb/key", "0x248")
        elif line == "B3=1" or line == 'I0=N:A25D07F8':
            #self.relay_toggle()
            nerve.query("http://panther:8888/devices/mysensors/12/3/toggle")
        elif line == "B2=1":
            nerve.events.publish(self.get_pathname() + '/B2', name='B2', value=True)
        elif line == "B1=1":
            nerve.query("/devices/player/sort")
        elif line == "B0=1":
            nerve.query("/devices/player/shuffle")
        elif line.startswith('I0=') and line[3] != 'x':
            nerve.events.publish(self.get_pathname() + '/ir', name='ir', value=line[3:])
        elif line.startswith('T0='):
            self.temp = float(line[3:])
            nerve.log('deskclock: ' + str(self.temp) + 'C', logtype='info')
            nerve.events.publish(self.get_pathname() + '/t0', name='t0', value=self.temp)


def normalize(string):
    s = unicodedata.normalize('NFKD', string)
    return s.encode('ascii', 'ignore').decode('ascii')


deskclock2 = DeskClock2(file="/dev/ttyACM0", baud=115200)
nerve.set_object('/devices/deskclock', deskclock2)
nerve.set_object('/devices/deskclock2', deskclock2)


