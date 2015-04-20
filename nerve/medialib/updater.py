#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import os.path

import time
import mimetypes
import traceback
import threading

import mutagen
import subprocess

import signal
import fcntl


class MediaUpdaterTask (nerve.Task):
    def __init__(self, path):
        nerve.Task.__init__(self, 'MediaUpdaterTask')
        self.db = nerve.Database('medialib.sqlite')
        self.path = path        #nerve.get_config("medialib_dirs")
        self.run_update = threading.Event()

    def run(self):
        """
        def handler(signum, frame):
            self.run_update.set()
        signal.signal(signal.SIGIO, handler)

        fd = os.open(FNAME,  os.O_RDONLY)
        fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
        fcntl.fcntl(fd, fcntl.F_NOTIFY,
        fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)
        """

        while True:
            row = self.db.get_single('info', 'name,value', self.db.inline_expr('name', 'last_updated'))
            if row is None or float(row[1]) + 86400 < time.time():
                nerve.log("Starting medialib update...")
                self.update_all()
                self.check_for_deleted()
                nerve.log("Medialib update complete")
                self.db.insert('info', { 'name' : 'last_updated', 'value' : str(time.time()) }, replace=True)
            if self.stopflag.wait(3600):
                break 

    def update_all(self):
        for libpath in self.path:
            for root, dirs, files in os.walk(libpath):
                if self.stopflag.is_set():
                    return
                nerve.log("Searching " + root)
                for media in files:
                    #if media.endswith('.mp3'):
                    self.update_file(os.path.join(root, media))

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

    def update_file(self, filename):
        (mimetype, encoding) = mimetypes.guess_type(filename)

        if not mimetype or (not mimetype.startswith('audio/') and not mimetype.startswith('video/')):
            return
        (media_type, _, _) = mimetype.partition('/')

        (mode, inode, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)

        rows = list(self.db.get('media', 'id,file_last_modified', self.db.inline_expr('filename', filename)))
        if len(rows) > 0 and mtime <= rows[0][1]:
            #nerve.log("Skipping " + filename)
            return

        try:
            meta = MetaData(filename, media_type)
        except:
            nerve.log(traceback.format_exc())
            return

        data = {
            'filename' : filename,
            'artist' : meta.get('artist'),
            'title' : meta.get('title'),
            'album' : meta.get('album'),
            'track_num' : meta.get('trackno'), #meta.get('tracknumber'),
            'genre' : meta.get('genre'),
            'tags' : '',
            'media_type' : media_type,
            'mimetype' : mimetype,
            'duration' : float(meta.get('length', default=-1)),
            'file_hash' : meta.get('hash'),
            'file_size' : size,
            'file_last_modified' : mtime,
        }
        if len(rows) <= 0:
            nerve.log("Adding " + filename)
            self.db.insert('media', data)
        else:
            nerve.log("Updating " + filename)
            self.db.where('id', rows[0][0])
            self.db.update('media', data)


class MetaData (object):
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
            (_, _, value) = self.filename.rpartition('/')
            (value, _, _) = value.rpartition('.')
            if self.media_type == 'audio':
                (_, _, value) = value.partition("-")
            return value
        elif name == 'artist' and self.media_type == 'audio':
            (_, _, value) = self.filename.rpartition('/')
            (value, _, _) = value.rpartition('.')
            (value, _, _) = value.partition("-")
            return value

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


