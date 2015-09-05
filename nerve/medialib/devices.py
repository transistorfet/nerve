#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import time
import random

from .playlists import Playlist


# TODO apart from the updater threads, there isn't really anything 'device' about this.  It's really a model isn't it?
# it reads info from a database, or from playlist files, acting as a counterpart to the medialib controller/UI
# the one thing that isn't like the only other model that exists in this system is the configuration data...  Should
# models be added to the object fs with config options, and everything uses the ofs to lookup the model?  Should they
# be created for each use (eg. for each controller that needs that model?)  The config is only for the updaters actually
# so...

class MediaLibDevice (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.playlists = 'playlists'
        self.db = nerve.Database('medialib.sqlite')
        self.db.create_table('media', "id INTEGER PRIMARY KEY, filename TEXT, artist TEXT, album TEXT, title TEXT, track_num NUMERIC, genre TEXT, tags TEXT, duration NUMERIC, media_type TEXT, mimetype TEXT, file_hash TEXT, file_size INT, file_last_modified INT")
        self.db.create_table('info', "name TEXT PRIMARY KEY, value TEXT")

        self.current = 'default'

    def force_database_update(self):
        self.db.where('name', 'last_updated')
        self.db.update('info', { 'value' : 0 })

    def rehash(self):
        self.force_database_update()

    def get_playlist_list(self):
        files = os.listdir(nerve.configdir() + '/playlists')
        playlist_list = [ name[:-4] for name in files if name.endswith(".m3u") ]
        if 'default' in playlist_list:
            playlist_list.remove('default')
        playlist_list.insert(0, 'default')
        return playlist_list

    def get_media_list(self, mode, order, offset, limit, search=None, recent=None, media_type=None):
        if mode == 'artist':
            self.db.select('artist')
            self.db.where_not('artist', '')
            self.db.group_by('artist')
        elif mode == 'album':
            self.db.select('artist,album')
            self.db.where_not('album', '')
            self.db.group_by('artist,album')
        elif mode == 'genre':
            self.db.select('artist,album,genre')
            self.db.group_by('artist,album')
        elif mode == 'title' or mode == 'tags':
            self.db.select('artist,album,title,track_num,tags,id')
        else:
            return [ ]

        if search and len(search) > 0:
            whereorder = order
            if order == 'modified':
                whereorder = 'file_last_modified'
            elif order == 'random':
                whereorder = 'title'
            self.db.where_like(whereorder, '%' + str(search).replace('*', '%') + '%')

        if order == 'artist':
            self.db.order_by('artist ASC')
        elif order == 'album':
            self.db.order_by('artist,album ASC')
        elif order == 'genre':
            self.db.order_by('genre,artist,album ASC')
        elif order == 'tags':
            self.db.order_by('tags,artist,album ASC')
        elif order == 'title':
            self.db.order_by('title,artist,album ASC')
        elif order == 'modified':
            self.db.order_by('file_last_modified DESC')
        elif order == 'filename':
            self.db.order_by('filename ASC')

        if recent:
            self.db.where_gt('file_last_modified', time.time() - (float(recent) * (60*60*24*7)))

        if media_type:
            self.db.where('media_type', media_type)

        result = list(self.db.get_assoc('media'))
        if order == 'random':
            random.shuffle(result)
        return result

    def get_media_query(self, criteria):
        if 'url' in criteria:
            return [{
                'id': -1,
                'filename': criteria['url'][0],
                'artist': criteria['artist'][0] if 'artist' in criteria else '',
                'album': criteria['album'][0] if 'album' in criteria else '',
                'title': criteria['title'][0] if 'title' in criteria else '',
                'duration': criteria['duration'][0] if 'duration' in criteria else 0
            }]

        self.db.select('id,filename,artist,album,title,duration')
        if 'artist' in criteria:
            self.db.where('artist', criteria['artist'][0])
            self.db.where_not('artist', '')
        if 'album' in criteria:
            self.db.where('album', criteria['album'][0])
            self.db.where_not('album', '')
        if 'id' in criteria:
            self.db.where('id', criteria['id'][0])
        self.db.order_by('artist,album,title ASC')
        result = list(self.db.get_assoc('media'))
        return result

    def get_playlist(self, name=None):
        if name is None:
            name = self.current
        playlist = Playlist(name)
        media_list = playlist.get_list()
        return media_list

    def sort_playlist(self, name=None):
        if name is None:
            name = self.current
        playlist = Playlist(name)
        playlist.sort()
        return playlist.get_size()

    def shuffle_playlist(self, name=None):
        if name is None:
            name = self.current
        playlist = Playlist(name)
        playlist.shuffle()
        return playlist.get_size()

    def get_media_info(self, media_list):
        info = [ ]
        for filename in media_list:
            self.db.select('id,filename,artist,album,title,track_num,genre,tags,duration')
            self.db.where('filename', filename)
            result = list(self.db.get_assoc('media'))
            if len(result) > 0:
                info.extend(list(result))
            else:
                info.append({
                    'id' : -1,
                    'filename' : filename,
                    'artist' : '',
                    'album' : '',
                    'title' : filename,
                    'track_num' : '',
                    'genre' : '',
                    'tags' : '',
                    'duration' : 0
                })
        return info


