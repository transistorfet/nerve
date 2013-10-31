
import serial

import nerve
from nerve.devices.winamp import Winamp
from nerve.devices.win32sys import Win32Sys

class Stereo (nerve.Device):
    def __init__(self, serial):
	self.serial = serial

    def power(self, msg):
	self.serial.send("ir S A81")

    def volup(self, msg):
	self.serial.send("ir S 481")

    def voldown(self, msg):
	self.serial.send("ir S C81")

    def tape(self, msg):
	self.serial.send("ir S C41")

    def tuner(self, msg):
	self.serial.send("ir S 841")


class Television (nerve.Device):
    def __init__(self, serial):
	self.serial = serial

    def power(self, msg):
	self.serial.send("ir P 4004 100BCBD")

    def volup(self, msg):
	self.serial.send("ir P 4004 1000405")

    def voldown(self, msg):
	self.serial.send("ir P 4004 1008485")

    def ps3(self, msg):
	self.serial.send("ir P 4004 100A0A1")
	self.serial.send("ir P 4004 1008889")

    def netbook(self, msg):
	self.serial.send("ir P 4004 100A0A1")
	self.serial.send("ir P 4004 1004849")


port = 5959

# Additional Device Ideas:
#   sys or misc or something for stuff like waking up the netbook screen, maybe sound output select

serv = nerve.Server(port)

nerve.add_device("layout", nerve.Layout())

rgbnode = nerve.NerveSerialDevice("COM9", 19200)
nerve.add_device("rgb", rgbnode)
nerve.add_device("stereo", Stereo(rgbnode))
nerve.add_device("tv", Television(rgbnode))

nerve.add_device("sys", Win32Sys())
nerve.add_device("music", Winamp())

nerve.loop()
 
"""
def dispatch(data, addr):
    (host, port) = addr
    msg = data.lower().strip('\n')
    print "RECV from " + str(host) + ":" + str(port) + ": " + msg

    words = msg.split()
    cmd = words[0].split('.')
    if cmd[0] == 'music':
	if cmd[1] == 'next':
	    music.next()
	elif cmd[1] == 'previous':
	    music.previous()
	elif cmd[1] == 'toggle':
	    s = music.getPlaybackStatus()
	    if s == winamp.Winamp.PLAYBACK_PLAYING or s == winamp.Winamp.PLAYBACK_PAUSE:
		music.pause()
	    elif s == winamp.Winamp.PLAYBACK_NOT_PLAYING:
		music.play()
	elif cmd[1] == 'getvolume':
	    volume = music.getVolume()
	    serv.send(str(volume), addr)
	elif cmd[1] == 'getsong':
	    song = music.getCurrentPlayingTitle()
	    serv.send(song, addr)
    elif cmd[0] == 'stereo':
	if cmd[1] == 'power':
	    arduino.write("CA\n")
	elif cmd[1] == 'volup':
	    arduino.write("CB\n")
	elif cmd[1] == 'voldown':
	    arduino.write("CC\n")
	elif cmd[1] == 'tape':
	    arduino.write("CD\n")
	elif cmd[1] == 'tuner':
	    arduino.write("CE\n")
    elif cmd[0] == 'tv':
	if cmd[1] == 'power':
	    arduino.write("Ca\n")
	elif cmd[1] == 'volup':
	    arduino.write("Cb\n")
	elif cmd[1] == 'voldown':
	    arduino.write("Cc\n")
	elif cmd[1] == 'ps3':
	    arduino.write("Cd\n")
	    arduino.write("Ce\n")
	elif cmd[1] == 'netbook':
	    arduino.write("Cd\n")
	    arduino.write("Cf\n")
"""


