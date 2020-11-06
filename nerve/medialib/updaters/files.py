#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import re
import os
import os.path

import time
import mimetypes
import traceback
import threading

#import mutagen
import subprocess

from ..threads import MediaLibUpdater

skiptypes = [
    'audio/x-mpegurl'
]

class MediaFilesUpdater (MediaLibUpdater):
    def __init__(self):
        super().__init__()
        self.db = nerve.Database('medialib.sqlite')
        #self.path = path        #nerve.get_config("medialib_dirs")
        self.paths = [ ]

    def reset_check(self):
        self.db.where('name', 'last_updated')
        self.db.update('info', { 'value' : 0 })

    def check_update(self):
        row = self.db.get_first_row('info', 'name,value', self.db.inline_expr('name', 'last_updated'))
        if row is None or float(row[1]) + 86400 < time.time():
            self.run_update()
            return

        lasttime = float(row[1])
        medialib = nerve.get_object('/modules/medialib')
        self.path = medialib.get_setting('medialib_dirs')

        for libpath in self.path:
            mtime = os.path.getmtime(libpath)
            # if the dir has changed since we last updated, it's been more than 10 minutes since our last update, and more than 2 minutes since the dir changed, then update
            if mtime > lasttime and mtime + 120 > time.time() and lasttime + 600 > time.time():
                self.run_update()

    def run_update(self):
        medialib = nerve.get_object('/modules/medialib')
        self.path = medialib.get_setting('medialib_dirs')
        self.ignore = medialib.get_setting('ignore_dirs')

        if not self.path:
            nerve.log("warning: medialib_dirs not set", logtype='warning')
            return

        nerve.log("Starting medialib update...")
        for libpath in self.path:
            for root, dirs, files in os.walk(libpath):
                if len(tuple(name for name in self.ignore if name in root)) > 0:
                    continue

                if self.stopflag.is_set():
                    return
                nerve.log("Searching " + root)
                for media in files:
                    #if media.endswith('.mp3'):
                    self.update_file(os.path.join(root, media), len(libpath.rstrip('/')) + 2)

        self.check_for_deleted()
        self.db.insert('info', { 'name' : 'last_updated', 'value' : str(time.time()) }, replace=True)
        nerve.log("Medialib update complete")
        #nerve.query('/devices/notify/send', 'medialib update complete')

    def check_for_deleted(self):
        for libpath in self.path:
            if not os.path.exists(libpath):
                continue
            self.db.select('id,filename')
            self.db.where_like('filename', libpath + '%')
            for row in self.db.get('media'):
                if not os.path.exists(row[1]):
                    nerve.log("Removing " + row[1] + " (id: " + str(row[0]) + ")")
                    self.db.where('id', row[0])
                    self.db.delete('media')

    def update_file(self, filename, rootlen):
        (mimetype, encoding) = mimetypes.guess_type(filename)

        if not mimetype or mimetype in skiptypes or (not mimetype.startswith('audio/') and not mimetype.startswith('video/')):
            return
        (media_type, _, _) = mimetype.partition('/')

        (mode, inode, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)

        existing_id = None
        rows = list(self.db.get('media', 'id,last_modified', self.db.inline_expr('filename', filename)))
        if len(rows) > 0:
            if rows[0][1] and mtime <= rows[0][1]:
                #nerve.log("Skipping " + filename)
                return
            existing_id = rows[0][0]

        try:
            meta = MetaData(filename, media_type)
        except:
            nerve.log(traceback.format_exc(), logtype='error')
            return

        file_hash = meta.get('hash')
        rows = list(self.db.get('media', 'id,filename', self.db.inline_expr('file_hash', file_hash)))
        if len(rows) > 0 and not os.path.exists(rows[0][1]):
            existing_id = rows[0][0]
            print("Using existing id: " + str(existing_id) + " " + str(rows[0][1]))

        data = {
            'filename' : filename,
            'rootlen' : rootlen,
            'artist' : meta.get('artist'),
            'title' : meta.get('title'),
            'album' : meta.get('album'),
            'track_num' : meta.get('trackno'), #meta.get('tracknumber'),
            'genre' : meta.get('genre'),
            'media_type' : media_type,
            'mimetype' : mimetype,
            'duration' : float(meta.get('length', default=-1)),
            'file_hash' : file_hash,
            'file_size' : size,
            'last_modified' : mtime,
        }
        if existing_id == None:
            nerve.log("Adding " + filename)
            data['tags'] = ''
            self.db.insert('media', data)
        else:
            nerve.log("Updating " + filename)
            self.db.where('id', existing_id)
            self.db.update('media', data)


class MetaData (object):
    formats = [
        ( re.compile(r'^(.*?)\s*-\s*(\d+)\s*-\s*(.*)\.(\w+)$'), lambda m: { 'artist': m.group(1), 'track_num': m.group(2), 'title': m.group(3) } ),
        ( re.compile(r'^(\d+)\s*-\s*(.*?)\s*-\s*(.*)\.(\w+)$'), lambda m: { 'track_num': m.group(1), 'artist': m.group(2), 'title': m.group(3) } ),
        ( re.compile(r'^(.*?)\s*-\s*(.*)\.(\w+)$'), lambda m: { 'artist': m.group(1), 'title': m.group(2) } ),
    ]

    def __init__(self, filename, media_type=None):
        self.filename = filename
        self.media_type = media_type
        self.meta = { }
        self.info = None

        """
        try:
            self.meta = mutagen.File(filename, None, True)
            if filename.endswith('.mp3'):
                self.info = mutagen.mp3.MP3(filename)
        except ValueError:
            pass
        """

        self.fetch_mminfo()

        (_, _, name) = self.filename.rpartition('/')
        (title, _, _) = name.rpartition('.')
        self.fninfo = { 'title': title }
        if self.media_type == 'audio':
            for fmt in self.formats:
                m = fmt[0].match(name)
                if m:
                    self.fninfo = fmt[1](m)
                    break

    def get(self, name, default=None):
        """
        if name == 'length' and self.info != None:
            return self.info.info.length
        if self.meta and name in self.meta and len(self.meta[name]) > 0:
            return self.meta[name][0]
        """

        if self.mminfo and name in self.mminfo and self.mminfo[name]:
            return self.mminfo[name]

        if name == 'genre':
            for segment in reversed(self.filename.split('/')):
                if segment.lower() in self.genres:
                    return self.genres[segment.lower()]
        elif name == 'title':
            #(_, _, value) = self.filename.rpartition('/')
            #(value, _, _) = value.rpartition('.')
            #if self.media_type == 'audio':
            #    (_, _, value) = value.partition("-")
            #return value
            return self.fninfo['title'] if 'title' in self.fninfo else ''
        elif name == 'artist' and self.media_type == 'audio':
            #(_, _, value) = self.filename.rpartition('/')
            #(value, _, _) = value.rpartition('.')
            #(value, _, _) = value.partition("-")
            #return value
            return self.fninfo['artist'] if 'artist' in self.fninfo else ''
        elif name == 'track_num' and self.media_type == 'audio':
            return self.fninfo['track_num'] if 'track_num' in self.fninfo else None

        return default

    def fetch_mminfo(self):
        proc = subprocess.Popen(["mminfo", self.filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()

        self.mminfo = { }
        (_, _, out) = out.partition(b'\n')
        lines = out.decode('utf-8').split('\n')
        for line in lines:
            if line and line.startswith('+'):
                break
            (name, sep, value) = line.partition(':')
            name = name.lstrip(' |')
            if name:
                self.mminfo[name] = value.lstrip()
        #print(self.mminfo)

    genres = {
        'documentaries' : "Documentary",
        'comedies' : "Comedy",
        'dramas' : "Drama",
        'tv shows' : "TV Show",
        'episodics' : "Episodic",
        'movies' : "Movie",
        'music videos' : "Music Video",
        'miscellaneous' : "Misc",
        'misc' : "Misc",
        'unsorted' : "Unsorted",
        'pop' : "Pop",
        'rock' : "Rock",
        'electronica' : "Electronica",
        'jazz' : "Jazz",
        'blues' : "Blues",
        'ambient' : "Ambient",
        'goth' : "Goth",
        'humor' : "Humor",
        'indie' : "Indie",
        'metal' : "Metal",
        'industrial' : "Industrial",
        'progressive' : "Progressive"
    }


