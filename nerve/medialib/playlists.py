#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import os.path
import random


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
 

