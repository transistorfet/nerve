
import nerve 
import serial
import thread
import select
import traceback

class SerialDevice (nerve.Device):
    def __init__(self, file, baud):
	self.file = file
	self.baud = baud
	self.serial = serial.Serial(file, baud)
	thread.start_new_thread(self.do_thread, (self,))

    def send(self, data):
	Console.log("SEND -> " + str(host) + ":" + str(port) + ": " + data)
	self.serial.write(data)

    def do_receive(self, msg):
	pass

    def do_idle(self):
	pass

    def do_thread(self, nothing):
	while 1:
	    try:
		self.do_idle()
		(rl, wl, el) = select.select([ self.serial ], [ ], [ ], 0.1)
		if rl and self.serial in rl:
		    line = self.serial.readline()
		    line = line.strip()
		    nerve.Console.log("RECV <- " + self.file + ": " + line)
		    # TODO this is very wrong below...
		    msg = nerve.Message("serial.in" + " " + line, None, self)
		    self.do_receive(msg)
	    except:
		t = traceback.format_exc()
		nerve.Console.log(t)


class Stereo (nerve.Device):
    def __init__(self, serial):
	self.serial = serial

    def power(self, msg):
	self.serial.write("IsA81\n")

    def volup(self, msg):
	self.serial.write("Is481\n")

    def voldown(self, msg):
	self.serial.write("IsC81\n")

    def tape(self, msg):
	self.serial.write("IsC41\n")

    def tuner(self, msg):
	self.serial.write("Is841\n")


class Television (nerve.Device):
    def __init__(self, serial):
	self.serial = serial

    def power(self, msg):
	self.serial.write("Ip4004,100BCBD\n")

    def volup(self, msg):
	self.serial.write("Ip4004,1000405\n")

    def voldown(self, msg):
	self.serial.write("Ip4004,1008485\n")

    def ps3(self, msg):
	self.serial.write("Ip4004,100A0A1\n")
	self.serial.write("Ip4004,1008889\n")

    def netbook(self, msg):
	self.serial.write("Ip4004,100A0A1\n")
	self.serial.write("Ip4004,1004849\n")


class RGBStrip (nerve.Device):
    def __init__(self, serial):
	self.serial = serial

    def power(self, msg):
	self.serial.write("Lx\n")

    def setchannel(self, msg):
	self.serial.write("C%s\n" % (msg.args[0],))

    def setindex(self, msg):
	self.serial.write("P%s\n" % (msg.args[0],))

    def setcolour(self, msg):
	self.serial.write("S%s\n" % (msg.args[0],))

    def getdelay(self, msg):
	# TODO how the f will this work?
	self.serial.write("D%s\n" % (msg.args[0],))

    def setdelay(self, msg):
	self.serial.write("D%s\n" % (msg.args[0],))



class Layout (nerve.Device):
    def _get_file_contents(self, filename):
	with open(filename, 'r') as f:
	    data = f.read()
	return data

    # When the phone requests layout.default, return the default layout XML file
    def livingroom(self, msg):
	contents = self._get_file_contents('layouts/livingroom.xml')
	msg.server.send(msg.query + " " + contents, msg.addr)

    def comproom(self, msg):
	contents = self._get_file_contents('layouts/comproom.xml')
	msg.server.send(msg.query + " " + contents, msg.addr)

    def general(self, msg):
	contents = self._get_file_contents('layouts/general.xml')
	msg.server.send(msg.query + " " + contents, msg.addr)

