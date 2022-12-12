#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import subprocess

import nerve


class MPC (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)

        self.artist = ""
        self.title = ""
        self.current_song = ""
        self.reply = None

    def toggle(self):
        os.system("mpc toggle")
        self.update_info()

    def next(self):
        os.system("mpc next")
        self.update_info()

    def previous(self):
        os.system("mpc prev")
        self.update_info()

    def sort(self):
        os.system("mpc playlist | sort | mpc add")

    def shuffle(self):
        os.system("mpc shuffle")

    def getsong(self):
        self.update_info()
        return self.current_song

    def update_info(self):
        proc = subprocess.Popen(["mpc", "current", "--format", "%artist% - %title%"], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        self.current_song = out.decode('utf-8')
        (self.artist, _, self.title) = self.current_song.partition(" - ")

    #def load_playlist(self, url):
    #    os.system("xmms2 clear")

    #    if url.find('/') < 0:
    #        url = nerve.files.find('playlists/' + url + '.m3u')

    #    with open(url, 'r') as f:
    #        for line in f.read().split('\n'):
    #            line = line.strip()
    #            if line and not line.startswith('#'):
    #                media_url = "file://" + line
    #                os.system("xmms2 add \"" + media_url + "\"")


