
import winamp

import win32api
import win32con

import device

class Winamp (device.Device):
    def __init__(self):
	self.winamp = winamp.Winamp()

    def next(self, msg):
	self.winamp.next()
	song = self.winamp.getCurrentPlayingTitle()
	msg.server.send('.'.join(msg.names[:-1]) + ".getsong " + song, msg.addr)

    def previous(self, msg):
	self.winamp.previous()
	song = self.winamp.getCurrentPlayingTitle()
	msg.server.send('.'.join(msg.names[:-1]) + ".getsong " + song, msg.addr)

    def toggle(self, msg):
	s = self.winamp.getPlaybackStatus()
	if s == winamp.Winamp.PLAYBACK_PLAYING or s == winamp.Winamp.PLAYBACK_PAUSE:
	    self.winamp.pause()
	elif s == winamp.Winamp.PLAYBACK_NOT_PLAYING:
	    self.winamp.play()

    def getvolume(self, msg):
	volume = self.winamp.getVolume()
	msg.server.send(msg.query + " " + str(volume), msg.addr)

    def getsong(self, msg):
	song = self.winamp.getCurrentPlayingTitle()
	msg.server.send(msg.query + " " + song, msg.addr)


class Win32Sys (device.Device):
    def wakeup(self, msg):
	win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
	win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

 
