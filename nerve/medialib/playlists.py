#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import os.path
import random


class Playlist (object):
    def __init__(self, name):
        self.name = name
        self.media_list = [ ]
        self.filename = nerve.files.find('playlists/' + name + '.m3u', create=True)

    @staticmethod
    def listnames():
        dirname = nerve.files.find('playlists')
        if not os.path.isdir(dirname):
            raise Exception(dirname + " is not a directory")
        files = os.listdir(dirname)
        return [ name[:-4] for name in files if name.endswith(".m3u") ]

    @staticmethod
    def create(name):
        nerve.files.createfile('playlists/' + name + '.m3u')

    @staticmethod
    def delete(name):
        try:
            filename = nerve.files.find('playlists/' + name + '.m3u')
            if os.path.isfile(filename):
                os.remove(filename)
        except OSError:
            pass

    def load(self):
        self.media_list = [ ]
        artist = ""
        title = ""
        duration = 0
        with open(self.filename, 'rt') as f:
            for line in f.read().split('\n'):
                line = line.strip()
                if line and line.startswith('#'):
                    if line.startswith('#EXTINF:'):
                        (duration, info) = line[8:].split(', ', 1)
                        parts = info.split(' - ', 1)
                        artist = parts[0] if len(parts) > 1 else ''
                        title = parts[1] if len(parts) > 1 else parts[0]
                elif line != '':
                    media = {
                        'artist' : artist,
                        'title' : title,
                        'duration' : duration,
                        'filename' : line
                    }
                    self.media_list.append(media)

    def save(self):
        with open(self.filename, 'wt') as f:
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
 

