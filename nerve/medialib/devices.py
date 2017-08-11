#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import time
import shlex
import random
import urllib.parse

from . import tasks
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
        self.db = nerve.Database('medialib.sqlite')
        self.db.create_table('media', "id INTEGER PRIMARY KEY, filename TEXT, rootlen INTEGER, artist TEXT, album TEXT, title TEXT, track_num NUMERIC, genre TEXT, tags TEXT, duration NUMERIC, media_type TEXT, mimetype TEXT, file_hash TEXT, file_size INTEGER, last_modified NUMERIC")
        self.db.create_table('info', "name TEXT PRIMARY KEY, value TEXT")

        tasks.start_updater([ 'medialib/updaters/files/MediaFilesUpdater', 'medialib/updaters/youtube/YoutubePlaylistUpdater' ])

    def rehash(self):
        tasks.run_updater()

    def search(self, mode, order, offset, limit, search=None, recent=None, media_type=None, tags=None):
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
        elif mode == 'title':
            self.db.select('artist,album,title,track_num,duration,tags,id')
        elif mode == 'filename':
            self.db.select('SUBSTR(filename, rootlen) AS filename,artist,album,title,track_num,duration,tags,id')
        else:
            return [ ]

        if search and len(search) > 0:
            #whereorder = order
            #if order == 'random':
            #    whereorder = 'title'
            searchterm = '%' + str(search).replace('*', '%') + '%'
            self.db.where_like('artist', searchterm)
            self.db.or_where_like('title', searchterm)
            self.db.or_where_like('album', searchterm)

        if tags and len(tags) > 0:
            tags = shlex.split(tags)
            for tag in tags:
                if tag[0] != '!':
                    self.db.where_like('tags', '%' + tag + '%')
                else:
                    self.db.where_not_like('tags', '%' + tag[1:] + '%')

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
        elif order == 'last_modified':
            self.db.order_by('last_modified DESC')
        elif order == 'filename':
            self.db.order_by('filename ASC')
        elif order == 'duration':
            self.db.order_by('duration ASC')

        if recent:
            self.db.where_gt('last_modified', time.time() - (float(recent) * (60*60*24*7)))

        if media_type:
            self.db.where('media_type', media_type)

        if offset:
            self.db.offset(offset)

        if limit:
            self.db.limit(limit)

        result = list(self.db.get_assoc('media'))
        if order == 'random':
            random.shuffle(result)
        return result

    def get_media_query(self, criteria):
        if type(criteria) == str:
            criteria = nerve.delistify(urllib.parse.parse_qs(criteria))

        if 'url' in criteria:
            return [{
                'id': -1,
                'filename': criteria['url'],
                'artist': criteria['artist'] if 'artist' in criteria else '',
                'album': criteria['album'] if 'album' in criteria else '',
                'title': criteria['title'] if 'title' in criteria else '',
                'duration': criteria['duration'] if 'duration' in criteria else 0
            }]

        self.db.select('id,filename,artist,album,title,duration')
        if 'artist' in criteria:
            self.db.where('artist', criteria['artist'])
            self.db.where_not('artist', '')
        if 'album' in criteria:
            self.db.where('album', criteria['album'])
            self.db.where_not('album', '')
        if 'title' in criteria:
            self.db.where('title', criteria['title'])
        if 'id' in criteria:
            self.db.where('id', criteria['id'])
        self.db.order_by('artist,album,title ASC')
        result = list(self.db.get_assoc('media'))
        return result

    def get_media_queries(self, criteria_list):
        media = [ ]
        for criteria in criteria_list:
            media.extend(self.get_media_query(criteria))
        return media

    # NOTE this is no longer used, now that we use extended m3u playlists to store metadata
    """
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
    """

    def add_tag(self, id, tag):
        self.db.select('tags')
        self.db.where('id', id)
        result = list(self.db.get('media'))
        if len(result) <= 0:
            return
        item_tags = set(self.split_tags(result[0][0]))
        item_tags.add(tag)
        self.db.where('id', id)
        self.db.update('media', { 'tags' : self.join_tags(sorted(item_tags)) })

    def remove_tag(self, id, tag):
        self.db.select('tags')
        self.db.where('id', id)
        result = list(self.db.get('media'))
        if len(result) <= 0:
            return
        item_tags = set(self.split_tags(result[0][0]))
        item_tags.remove(tag)
        self.db.where('id', id)
        self.db.update('media', { 'tags' : self.join_tags(sorted(item_tags)) })

    @staticmethod
    def split_tags(tags):
        tagnames = [ ]
        while tags:
            tags = tags.lstrip(' ')
            if tags[0] == '"':
                (newtag, _, remaining) = tags[1:].partition('"')
            else:
                (newtag, _, remaining) = tags.partition(' ')
            tagnames.append(newtag)
            tags = remaining
        return tagnames

    @staticmethod
    def join_tags(tags):
        tagstring = ''
        for tag in tags:
            if ' ' in tag:
                tagstring += '"' + tag + '" '
            else:
                tagstring += tag + ' '
        return tagstring.rstrip()


class PlaylistsDevice (nerve.Device):
    def __init__(self, **config):
        super().__init__(**config)
        self.current = 'default'

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            pass
        return Playlist(name)

    """
    def set_child(self, index, obj):
        pass

    def del_child(self, index):
        return False
    """

    def get_playlist_list(self):
        playlist_list = Playlist.listnames()
        if 'default' in playlist_list:
            playlist_list.remove('default')
        playlist_list.insert(0, 'default')
        return playlist_list

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


