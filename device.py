 

class Namespace (object):
    def __init__(self):
	self.devices = { }

    def add(self, name, dev):
	self.devices[name] = dev

    def get(self, name):
	if name in self.devices:
	    return self.devices[name]
	return None

    def dispatch(self, msg):
	if len(msg.names) != 2:
	    return
	dev = self.devices[msg.names[0]]
	func = getattr(dev, msg.names[1])
	return func(msg)

	#obj = self.devices
	#for i in range(0, len(msg.names)):
	#    sub = obj[msg.names[i]]
	#    if isinstance(sub, Namespace):
	#	if i == len(msg.names) - 1:
	#	    raise InvalidRequest()
	#	obj = sub.devices
	#    elif isinstance(sub, types.MethodType):
	#	return sub(self, msg)


class Device (object):
    def __init__(self):
	pass

class SerialDevice (Device):
    def __init__(self, conn):
	self.serial = conn

class Stereo (SerialDevice):
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

class Television (SerialDevice):
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

class RGBStrip (SerialDevice):
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

