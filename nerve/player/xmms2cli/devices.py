#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import subprocess

import nerve


class Xmms2CLI (nerve.Device):
    def __init__(self, **config):
        nerve.Device.__init__(self, **config)

        self.title = ""
        self.current_song = ""
        self.reply = None

    def toggle(self):
        os.system("xmms2 toggle")
        self.update_info()

    def next(self):
        os.system("xmms2 next")
        self.update_info()

    def previous(self):
        os.system("xmms2 prev")
        self.update_info()

    def sort(self):
        os.system("xmms2 playlist sort url")

    def shuffle(self):
        os.system("xmms2 playlist shuffle")

    def getsong(self):
        self.update_info()
        return self.current_song

    def update_info(self):
        proc = subprocess.Popen(["xmms2", "current"], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        parts = out.decode('utf-8').split(':', 2)
        (self.current_song, _, _) = parts[1].strip().rpartition('.')
        (self.artist, _, self.title) = self.current_song.partition(" - ")

    def load_playlist(self, url):
        os.system("xmms2 clear")

        if url.find('/') < 0:
            url = nerve.configdir() + '/playlists/' + url + '.m3u'

        with open(url, 'r') as f:
            for line in f.read().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    media_url = "file://" + line
                    os.system("xmms2 add \"" + media_url + "\"")


