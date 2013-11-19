
import nerve
from nerve.devices.xmms2 import Xmms2

import time

class DeskClock (nerve.SerialDevice):
    def __init__(self, file, baud):
	nerve.SerialDevice.__init__(self, file, baud)
	self.relay1 = False

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


serv = nerve.Server(5959)

nerve.add_device("deskclock", DeskClock("/dev/ttyACM0", 19200))

nerve.add_device("rgb", nerve.NerveSerialDevice("/dev/ttyACM1", 19200))
nerve.add_device("music", Xmms2())

nerve.loop()


