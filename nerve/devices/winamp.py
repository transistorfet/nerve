
from support import winamp

import nerve

class Winamp (nerve.Device):
    def __init__(self):
	nerve.Device.__init__(self)
	self.winamp = winamp.Winamp()

    def next(self, msg):
	self.winamp.next()
	song = self.winamp.getCurrentPlayingTitle()
	msg.reply(msg.devname() + ".getsong " + song)

    def previous(self, msg):
	self.winamp.previous()
	song = self.winamp.getCurrentPlayingTitle()
	msg.reply(msg.devname() + ".getsong " + song)

    def toggle(self, msg):
	s = self.winamp.getPlaybackStatus()
	if s == winamp.Winamp.PLAYBACK_PLAYING or s == winamp.Winamp.PLAYBACK_PAUSE:
	    self.winamp.pause()
	elif s == winamp.Winamp.PLAYBACK_NOT_PLAYING:
	    self.winamp.play()

    def getvolume(self, msg):
	volume = self.winamp.getVolume()
	msg.reply(msg.query + " " + str(volume))

    def getsong(self, msg):
	song = self.winamp.getCurrentPlayingTitle()
	msg.reply(msg.query + " " + song)


