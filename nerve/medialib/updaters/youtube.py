#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.medialib

import time
import requests
import json

from ..tasks import MediaLibUpdater


class YoutubePlaylistUpdater (MediaLibUpdater):
    def __init__(self):
        super().__init__()
        self.db = nerve.Database('medialib.sqlite')
        self.json = None
        #self.list_ids = path        #nerve.get_config("youtube_playlists")
        self.list_ids = [ ]

    def reset_check(self):
        self.db.where('name', 'youtube_last_updated')
        self.db.update('info', { 'value' : 0 })

    def check_update(self):
        row = self.db.get_first_row('info', 'name,value', self.db.inline_expr('name', 'youtube_last_updated'))
        if row is None or float(row[1]) + 86400 < time.time():
            self.run_update()

    def run_update(self):
        medialib = nerve.get_object('/modules/medialib')
        self.list_ids = medialib.get_setting('youtube_playlists')
        if not self.list_ids:
            nerve.log("warning: youtube_playlists not set", logtype='warning')
            return

        nerve.log("Starting youtube medialib update...")
        for list_id in self.list_ids:
            json_playlist = self.fetch_json(list_id)
            if json_playlist is None or 'video' not in json_playlist:
                nerve.log("Unable to fetch youtube playlist " + list_id, logtype='error')
            else:
                playlist = [ ]
                for video in json_playlist['video']:
                    if self.stopflag.is_set():
                        return
                    data = self.hash_video(video)
                    playlist.append({ 'artist' : data['artist'], 'title' : data['title'], 'duration' : data['duration'], 'filename' : data['filename'] })
                pl = nerve.medialib.Playlist(json_playlist['title'])
                pl.set_list(playlist)

        self.db.insert('info', { 'name' : 'youtube_last_updated', 'value' : str(time.time()) }, replace=True)
        nerve.log("Youtube medialib update complete")

    def fetch_json(self, list_id):
        url = 'http://www.youtube.com/list_ajax?action_get_list=1&style=json&list=%s' % (list_id,)
        try:
            r = requests.get(url)
            if r.text:
                return json.loads(r.text)
        except:
            nerve.log("error fetching youtube list " + list_id, logtype='error')
        return None

    def hash_video(self, meta):
        url = 'http://www.youtube.com/watch?v=%s' % (meta['encrypted_id'],)

        parts = meta['title'].split("-", 1)
        if len(parts) < 2:
            artist = ''
            title = meta['title']
        else:
            artist = parts[0].strip()
            title = parts[1].strip()
        data = {
            'filename' : url,
            'rootlen' : 0,
            'artist' : artist,
            'title' : title,
            'album' : 'YouTube',
            'track_num' : '',
            'genre' : '',
            'tags' : meta['keywords'],
            'media_type' : 'video',
            'duration' : float(meta['length_seconds']),
            'file_size' : '',
            'last_modified' : meta['time_created'],
        }

        rows = list(self.db.get('media', 'id,last_modified', self.db.inline_expr('filename', url)))
        if len(rows) > 0 and rows[0][1] >= meta['time_created']:
            #nerve.log("Skipping " + url)
            return data

        if len(rows) <= 0:
            nerve.log("Adding " + url)
            self.db.insert('media', data)
        else:
            nerve.log(u"Updating " + url)
            self.db.where('id', rows[0][0])
            self.db.update('media', data)
        return data

 

