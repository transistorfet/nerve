#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import subprocess
import os
import sys
import time
import socket
import traceback
import platform

import urllib.parse
import requests
import json

class PlayerDevice (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.driver = None

        backend_name = self.get_setting('backend')
        try:
            (empty, sep, type_name) = backend_name.partition("/modules/player/")
            if empty == '' and sep and type_name:
                print(type_name)
                (module_name, sep, player_obj) = type_name.rpartition('/')
                nerve.ModulesDirectory.import_module("player." + module_name.replace('/', '.'))
                self.driver = nerve.ObjectNode.make_object("player/" + type_name, config)
        except:
            nerve.log("failed to initialize player backend: " + backend_name)
            nerve.log(traceback.format_exc())

        self.playlist = []

    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        config_info.add_setting('backend', "Player Backend", default='player.vlc')
        for option in os.listdir('nerve/player'):
            if option != '__pycache__' and os.path.isdir('nerve/player/' + option):
                config_info.add_option('backend', option, '/modules/player/' + option)
        return config_info

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            pass
        return getattr(self.driver, name)

    """
    def next(self):
        self._send_command('pl_next')
        self.next_update = time.time() + 2

    def previous(self):
        self._send_command('pl_previous')
        self.next_update = time.time() + 2

    def toggle(self):
        self._send_command('pl_pause')

    def getvolume(self):
        if self.status is not None:
            return self.status['volume']
        return 0

    def setvolume(self, volume):
        self._send_command('volume', volume)

    def volume(self, volume=None):
        if volume:
            self._send_command('volume', volume)
        return self.getvolume()

    def volup(self):
        if not self.status:
            return
        volume = int(self.status['volume']) + 5
        if volume > 256:
            volume = 256
        self._send_command('volume', volume)

    def voldown(self):
        if not self.status:
            return
        volume = int(self.status['volume']) - 5
        if volume < 0:
            volume = 0
        self._send_command('volume', volume)

    def random(self):
        self._send_command('pl_random')

    def fullscreen(self):
        self._send_command('fullscreen')

    def enable_video(self):
        self._send_command('video_track', 0)

    def disable_video(self):
        self._send_command('video_track', -1)

    def getsong(self):
        if self.status is not None:
            return self._get_title()
        return ""

    def clear_playlist(self):
        self._send_command('pl_empty')

    def getplaylist(self):
        r = requests.get('http://%s/requests/playlist.json' % (self.server,), auth=('', 'test'))
        self.playlist = json.loads(r.text)
        return self.read_playlist(self.playlist)

    def read_playlist(self, playlist):
        if playlist['type'] == 'leaf':
            return
        ret = [ ]
        for song in playlist['children']:
            if song['type'] == 'node':
                ret.extend(self.read_playlist(song))
            else:
                ret.append(song)
        return ret

    def playlist_seek(self, id):
        url = 'http://%s/requests/status.json?command=pl_play&id=%s' % (self.server, id)
        r = requests.get(url, auth=('', 'test'))

    def play(self, url):
        self._send_command_and_uri('in_play', urllib.parse.quote(url))

    def load_playlist(self, url):
        self._send_command('pl_empty')
        if url.find('/') < 0:
            url = nerve.configdir() + '/playlists/' + url + '.m3u'
        self._send_command_and_uri('in_play', urllib.parse.quote(url))

    def kill_instance(self):
        if self.proc is not None:
            self.proc.kill()
            self.proc = None
            self.next_update = time.time()
    """


