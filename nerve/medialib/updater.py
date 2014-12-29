# -*- coding: utf-8 -*-
#!/usr/bin/python

import nerve

import time
import os
import os.path
import mutagen


class MediaUpdaterTask (nerve.Task):
    def __init__(self, medialib, path):
	nerve.Task.__init__(self, 'MediaUpdaterTask')
	self.medialib = medialib
	self.db = nerve.DatabaseCursor(self.medialib.dbconnection)
	self.path = path	#nerve.get_config("medialib_dirs")

    def update_file(self, filename):
	(mode, inode, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)

	safe_filename = filename
	if isinstance(filename, unicode):
	    safe_filename = filename.encode('utf-8', 'replace')

	rows = list(self.db.get('media', 'id,file_last_modified', self.db.inline_expr('filename', filename)))
	if len(rows) > 0 and mtime <= rows[0][1]:
	    #nerve.log("Skipping " + safe_filename)
	    return

	meta = MetaData(filename)
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
	    nerve.log("Adding " + safe_filename)
	    self.db.insert('media', data)
	else:
	    nerve.log(u"Updating " + safe_filename)
	    self.db.where('id', rows[0][0])
	    self.db.update('media', data)

    def update_all(self):
	nerve.log("Starting medialib update...")
	for libpath in self.path:
	    for root, dirs, files in os.walk(unicode(libpath)):
		if self.stopflag.is_set():
		    return
		nerve.log("Searching " + root)
		for media in files:
		    if media.endswith('.mp3'):
			self.update_file(os.path.join(root, media))
	nerve.log("Medialib update complete")

    def run(self):
	while True:
	    row = self.db.get_single('info', 'name,value', self.db.inline_expr('name', 'last_updated'))
	    if row is None or float(row[1]) + 86400 < time.time():
		self.update_all()
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
	    return self.meta[name][0].encode('utf-8', 'replace')
	return default


