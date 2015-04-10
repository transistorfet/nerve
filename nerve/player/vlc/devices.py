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

class VLCHTTP (nerve.Device):
    def __init__(self, **config):
        nerve.Device.__init__(self, **config)
        self.proc = None
        self.status = None
        self.lastplid = 0
        self.lastmsg = None
        self.next_update = 0

        self.server = 'localhost:8081'
        self.auth = ('', 'test')

        self.thread = nerve.Task('VLCTask', self.run)
        self.thread.start()

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

        for sublist in self.playlist['children']:
            if sublist['name'] == "Playlist":
                #self.playlist = sublist['children']
                break

        return self._read_playlist(self.playlist)

    def _read_playlist(self, playlist):
        if playlist['type'] == 'leaf':
            return
        ret = [ ]
        for song in playlist['children']:
            if song['type'] == 'node':
                ret.extend(self._read_playlist(song))
            else:
                ret.append(song)
        return ret

    def current_playlist(self):
        # TODO return the name of the current playlist that the player is playing, such that you can match it with the playlists in medialib
        pass

    def get_position(self):
        # TODO read the playlist position so that you can have the playlist display and anchor in the playlist webpage
        pass

    def playlist_seek(self, id):
        url = 'http://%s/requests/status.json?command=pl_play&id=%s' % (self.server, id)
        r = requests.get(url, auth=('', 'test'))

    def play(self, url):
        self._send_command_and_uri('in_play', urllib.parse.quote(url))

    def enqueue(self, url):
        self._send_command_and_uri('in_enqueue', urllib.parse.quote(url))

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
    def command(self, msg):
        #self.client.send(' '.join(msg.args))
        if len(msg.args) == 1:
            self._send_command(msg.args[0])
        else:
            self._send_command(msg.args[0], msg.args[1])
    """

    def _send_command(self, cmd, val=None):
        url = 'http://%s/requests/status.json?command=%s' % (self.server, cmd)
        if val is not None:
            url += '&val=' + str(val)
        r = requests.get(url, auth=('', 'test'))

    def _send_command_and_uri(self, cmd, media_uri):
        url = 'http://%s/requests/status.json?command=%s&input=%s' % (self.server, cmd, media_uri)
        r = requests.get(url, auth=('', 'test'))

    def _get_title(self):
        if self.status is None or 'information' not in self.status:
            return '(no data)'
        meta = self.status['information']['category']['meta']
        if 'artist' in meta and 'title' in meta:
            return meta['artist'] + " - " + meta['title']
        else:
            return meta['filename']

    def run(self):
        retry_counter = 0

        while not self.thread.stopflag.wait(1):
            if self.proc is None:
                self.proc = self.launch_vlc_instance()
                time.sleep(5)        # wait for vlc to start before requesting

            current_time = time.time()
            if current_time < self.next_update:
                continue
            self.next_update = current_time + 30

            try:
                r = requests.get('http://%s/requests/status.json' % (self.server,), auth=('', 'test'))
                r.encoding = 'utf-8'
                if r.text:
                    self.status = json.loads(r.text)
                #print (r.text)

                if self.status['currentplid'] != self.lastplid:
                    self.lastplid = self.status['currentplid']
                    if self.lastmsg is not None:
                        self.lastmsg.reply(self.device_name() + ".getsong " + self._get_title())

            except requests.ConnectionError:
                nerve.log("Error connecting to vlc http server...")
                retry_counter += 1
                if retry_counter >= 3:
                    retry_counter = 0
                    self.proc = None
                    self.next_update = 4

            except:
                t = traceback.format_exc()
                nerve.log(t)


        nerve.log("killing VLC process")
        if self.proc is not None:
            self.proc.terminate()

    def launch_vlc_instance(self):
        while not self.thread.stopflag.is_set():
            try:
                nerve.log("Starting new instance of VLC")
                # TODO make this more robust
                cmdoptions = " --extraintf http --http-port 8081 --http-password test"
                if platform.system() == 'Windows':
                    cmdline = "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" + cmdoptions
                    # TODO the creationnflags is apparently a hax to get a detached process, but i'm not sure if it works or is needed
                    proc = subprocess.Popen(cmdline.split(' '), stdin=None, stdout=None, stderr=None, close_fds=True, creationflags=0x08)
                else:
                    cmdline = "/usr/bin/vlc" + cmdoptions
                    #cmdline = cmd + " --extraintf rc --rc-host localhost:4212"
                    #proc = subprocess.Popen(cmdline.split(' '), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    #proc = subprocess.Popen(cmdline.split(' '), stdin=None, stdout=None, stderr=None, close_fds=True)
                    proc = subprocess.Popen(cmdline.split(' '), stdin=None, stdout=None, stderr=None, close_fds=True)
                return proc
            except:
                t = traceback.format_exc()
                nerve.log(t)
            # if the process fails to launch, we sleep for a while and then try again
            time.sleep(7)


 
