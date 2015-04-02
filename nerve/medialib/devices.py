#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import os
import os.path

import urllib
import random

from .updater import MediaUpdaterTask
from .youtube import YoutubePlaylistFetcher


class MediaLib (nerve.Device):
    def __init__(self, **config):
        nerve.Device.__init__(self, **config)
        self.playlists = 'playlists'
        self.dbconnection = nerve.Database('medialib.sqlite')
        self.db = nerve.DatabaseCursor(self.dbconnection)
        self.db.create_table('media', "id INTEGER PRIMARY KEY, filename TEXT, artist TEXT, album TEXT, title TEXT, track_num NUMERIC, genre TEXT, tags TEXT, duration NUMERIC, media_type TEXT, file_hash TEXT, file_size INT, file_last_modified INT")
        self.db.create_table('info', "name TEXT PRIMARY KEY, value TEXT")

        self.current = 'default'

        self.thread = MediaUpdaterTask(self, self.get_setting("medialib_dirs"))
        self.thread.start()

        self.thread = YoutubePlaylistFetcher(self, self.get_setting("youtube_playlists"))
        self.thread.start()

    def get_playlist_list(self):
        files = os.listdir(nerve.configdir() + '/playlists')
        playlist_list = [ name[:-4] for name in files if name.endswith(".m3u") ]
        try:
            playlist_list.remove('default')
        except ValueError:
            pass
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
            self.db.where_like(whereorder, search)

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

        if recent:
            self.db.where_gt('file_last_modified', time.time() - (float(recent) * (60*60*24*7)))

        if media_type:
            self.db.where('media_type', media_type)

        result = list(self.db.get_assoc('media'))
        if order == 'random':
            random.shuffle(result)
        return result

    def get_media_query(self, criteria):
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


class Playlist (object):
    def __init__(self, name):
        self.name = name
        plroot = nerve.configdir() + '/playlists'
        if not os.path.isdir(plroot):
            os.mkdir(plroot)
        self.filename = plroot + '/' + name + '.m3u'
        #if not os.path.isfile(self.filename):
        #    raise Exception(self.filename + " playlist not found")
        if not os.path.isfile(self.filename):
            with open(self.filename, 'w') as f:
                pass
        self.media_list = [ ]

    @staticmethod
    def create(self, name):
        plroot = nerve.configdir() + '/playlists'
        filename = plroot + '/' + name + '.m3u'
        if not os.path.isfile(filename):
            with open(filename, 'w') as f:
                pass

    @staticmethod
    def delete(name):
        plroot = nerve.configdir() + '/playlists'
        filename = plroot + '/' + name + '.m3u'
        if os.path.isdir(plroot) and os.path.isfile(filename):
            os.remove(filename)

    def load(self):
        self.media_list = [ ]
        artist = ""
        title = ""
        duration = 0
        with open(self.filename, 'r') as f:
            for line in f.read().split('\n'):
                line = line.strip()
                if line and line.startswith('#'):
                    if line.startswith('#EXTINF:'):
                        (duration, info) = line[8:].split(', ', 1)
                        (artist, title) = info.split(' - ', 1)
                elif line != '':
                    media = {
                        'artist' : artist,
                        'title' : title,
                        'duration' : duration,
                        'filename' : line
                    }
                    self.media_list.append(media)

    def save(self):
        with open(self.filename, 'w') as f:
            f.write("#EXTM3U\n")
            for media in self.media_list:
                f.write("#EXTINF:%d, %s - %s\n" % (float(media['duration']), media['artist'], media['title']))
                f.write(media['filename'] + "\n")

    def get_size(self):
        self.load()
        return len(self.media_list)

    def get_list(self):
        self.load()
        return self.media_list

    def set_list(self, media_list):
        self.media_list = media_list
        self.save()
        return len(self.media_list)

    def add_list(self, media_list):
        self.load()
        existing = len(self.media_list)
        self.media_list.extend(media_list)
        self.save()
        return len(self.media_list) - existing

    def remove_files(self, file_list):
        self.load()
        existing = len(self.media_list)

        media_list = [ ]
        for media in self.media_list:
            if media['filename'] in file_list:
                file_list.remove(media['filename'])
            else:
                media_list.append(media)
        self.media_list = media_list
        self.save()
        return existing - len(self.media_list)

    def clear(self):
        self.media_list = [ ]
        self.save()

    def shuffle(self):
        self.load()
        random.shuffle(self.media_list)
        self.save()

    def sort(self):
        self.load()
        self.media_list = sorted(self.media_list, key=lambda media: media['filename'])
        self.save()

