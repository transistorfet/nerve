
import serial

import nerve

import device
import device_win32

port = 5959

# Additional Device Ideas:
#   sys or misc or something for stuff like waking up the netbook screen, maybe sound output select

serv = nerve.Server(port)

arduino = serial.Serial("COM9", 19200)
nerve.add_device("stereo", device.Stereo(arduino))
nerve.add_device("tv", device.Television(arduino))
nerve.add_device("rgb", device.RGBStrip(arduino))

nerve.add_device("sys", device_win32.Win32Sys())
nerve.add_device("music", device_win32.Winamp())

nerve.add_device("layout", device.Layout())

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


