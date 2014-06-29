#!/usr/bin/python
# -*- coding: utf-8 -*-

import winampapi

import nerve

import time

class Winamp (nerve.Device):
    def __init__(self):
	nerve.Device.__init__(self)
	self.winamp = winampapi.Winamp()

    def next(self, msg):
	self.winamp.next()
	song = self.winamp.getCurrentPlayingTitle()
	msg.reply(msg.device_name() + ".getsong " + song)

    def previous(self, msg):
	self.winamp.previous()
	song = self.winamp.getCurrentPlayingTitle()
	msg.reply(msg.device_name() + ".getsong " + song)

    def toggle(self, msg):
	s = self.winamp.getPlaybackStatus()
	if s == winampapi.Winamp.PLAYBACK_PLAYING or s == winampapi.Winamp.PLAYBACK_PAUSE:
	    self.winamp.pause()
	elif s == winampapi.Winamp.PLAYBACK_NOT_PLAYING:
	    self.winamp.play()

    def getvolume(self, msg):
	volume = self.winamp.getVolume()
	msg.reply(msg.query + " " + str(volume))

    def getsong(self, msg):
	song = self.winamp.getCurrentPlayingTitle()
	song = song.encode("ascii", "replace")
	msg.reply(msg.query + " " + song)

    def mediaquery(self, msg):
	result = self.winamp.query(msg.args[0])
	line = ""
	for entry in result:
	    line += entry + "\n"
	msg.reply(msg.query + " " + line)

    def addalbum(self, msg):
	files = self.query("album = \"%s\"" % msg.args[0])
	for name in files:
	    self.winamp.enqueueFile(name)

