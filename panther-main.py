
import serial

import server
import device
import device_linux

devices = device.Namespace()

def initialize():
    deskclock = serial.Serial("/dev/ttyACM0", 19200)
    devices.add("rgb", device.RGBStrip(deskclock))

    devices.add("music", device_linux.Xmms2())


def main():
    serv = server.Server(5959, devices.dispatch)
    initialize()

    while 1:
	line = raw_input(">> ")
	if line == 'quit':
	    break

main()


