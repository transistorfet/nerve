#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import time
import os
import os.path
import mutagen


class MediaUpdaterTask (nerve.Task):
    def __init__(self, medialib, path):
        nerve.Task.__init__(self, 'MediaUpdaterTask')
        self.medialib = medialib
        self.db = self.medialib.db
        self.path = path        #nerve.get_config("medialib_dirs")

    def update_file(self, filename):
        (mode, inode, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)

        rows = list(self.db.get('media', 'id,file_last_modified', self.db.inline_expr('filename', filename)))
        if len(rows) > 0 and mtime <= rows[0][1]:
            #nerve.log("Skipping " + filename)
            return

        try:
            meta = MetaData(filename)
        except:
            return

        data = {
            'filename' : filename,
            'artist' : meta.get('artist'),
            'title' : meta.get('title'),
            'album' : meta.get('album'),
            'track_num' : meta.get('tracknumber'),
            'genre' : meta.get('genre'),
            'tags' : '',
            'media_type' : 'audio',
            'duration' : float(meta.get('duration', default=-1)),
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

    def update_all(self):
        for libpath in self.path:
            for root, dirs, files in os.walk(libpath):
                if self.stopflag.is_set():
                    return
                nerve.log("Searching " + root)
                for media in files:
                    if media.endswith('.mp3'):
                        self.update_file(os.path.join(root, media))

    def check_for_deleted(self):
        for libpath in self.path:
            self.db.select('id,filename')
            self.db.where_like('filename', libpath + '%')
            for row in self.db.get('media'):
                if not os.path.exists(row[1]):
                    nerve.log("Removing " + row[1] + " (id: " + str(row[0]) + ")")
                    self.db.where('id', row[0])
                    self.db.delete('media')

    def run(self):
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


class MetaData (object):
    def __init__(self, filename):
        self.filename = filename
        self.meta = { }
        self.info = None
        try:
            self.meta = mutagen.File(filename, None, True)
            if filename.endswith('.mp3'):
                self.info = mutagen.mp3.MP3(filename)
        except ValueError:
            pass

    def get(self, name, default=None):
        if name == 'duration' and self.info != None:
            return self.info.info.length
        if self.meta and name in self.meta and len(self.meta[name]) > 0:
            return self.meta[name][0]
        return default


