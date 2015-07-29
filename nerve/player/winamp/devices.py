#!/usr/bin/python3
# -*- coding: utf-8 -*-

import winampapi

import nerve

import time

class Winamp (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.winamp = winampapi.Winamp()

    def next(self):
        self.winamp.next()

    def previous(self):
        self.winamp.previous()

    def toggle(self):
        s = self.winamp.getPlaybackStatus()
        if s == winampapi.Winamp.PLAYBACK_PLAYING or s == winampapi.Winamp.PLAYBACK_PAUSE:
            self.winamp.pause()
        elif s == winampapi.Winamp.PLAYBACK_NOT_PLAYING:
            self.winamp.play()

    def getvolume(self):
        return self.winamp.getVolume()

    def getsong(self):
        song = self.winamp.getCurrentPlayingTitle()
        return song.encode("ascii", "replace")


