# -*- coding: utf-8 -*-
#!/usr/bin/python

import nerve

import time
import os
import os.path
import mutagen

import urllib
import codecs
import random

import requests
import json


class Playlist (object):
    def __init__(self, name):
	self.name = name
	plroot = nerve.configdir() + '/playlists'
	if not os.path.isdir(plroot):
	    os.mkdir(plroot)
	self.filename = plroot + '/' + name + '.m3u'

    def get_files(self):
	with codecs.open(self.filename, 'r', encoding='utf-8') as f:
	    contents = [ media for media in f.read().split('\n') if media ]
	return contents

    def set_files(self, media_list):
	with codecs.open(self.filename, 'w', encoding='utf-8') as f:
	    f.write('\n'.join(media_list))

    def add_files(self, media_list):
	with codecs.open(self.filename, 'a', encoding='utf-8') as f:
	    f.write('\n' + '\n'.join(media_list))

    def remove_files(self, media_list):
	existing_list = self.get_files()
	new_list = [ existing for existing in existing_list if existing not in media_list ]
	self.set_files(new_list)
	return len(existing_list) - len(new_list)

    def clear_playlist(self):
	with codecs.open(self.filename, 'w', encoding='utf-8') as f:
	    f.write('')


class MediaLib (nerve.Device):
    def __init__(self, path=None):
	nerve.Device.__init__(self)
	self.playlists = 'playlists'
	self.dbconnection = nerve.Database('medialib.sqlite')
	self.db = nerve.DatabaseCursor(self.dbconnection)
	self.db.create_table('media', "id INTEGER PRIMARY KEY, filename TEXT, artist TEXT, album TEXT, title TEXT, track_num NUMERIC, genre TEXT, tags TEXT, duration NUMERIC, media_type TEXT, file_hash TEXT, file_size INT, file_last_modified INT")

	self.current = 'Default'

	# TODO reenable after testing
	#self.path = [ '/media/media/Torrents' ]
	#self.path = [ '/media/media/Music', '/media/media/Torrents' ]
	self.path = [ 'Y:\Torrents', 'Y:\Music' ]
	#self.thread = MediaUpdaterTask(self, self.path)
	#self.thread.start()

	#self.thread = YoutubePlaylistFetcher([ 'PL303Lldd6pIgDFgO9RWRXLnXiBcnAqJW4', 'FL_VkJGWFV9ZEIv87E-0NM5w', 'PLDY5kejDqaCcKT2lRKFBeY7cy6BrHKeN0' ], self)
	#self.thread.start()

    def html_make_playlist(self, postvars):
	playlist = Playlist(self.current)
	files = [ ]
	if 'pl_replace' in postvars or 'pl_enqueue' in postvars:
	    if 'artist' in postvars:
		for artist in postvars['artist']:
		    self.db.select('filename')
		    self.db.where('artist', urllib.unquote(artist))
		    self.db.order_by('filename ASC')
		    for media in self.db.get('media'):
			files.append(media[0])

	    elif 'album' in postvars:
		for pair in postvars['album']:
		    artist, foo, album = pair.partition(" - ")

		    if artist and album:
			self.db.select('filename')
			self.db.where('artist', urllib.unquote(artist))
			self.db.where('album', urllib.unquote(album))
			self.db.order_by('filename ASC')
			for media in self.db.get('media'):
			    files.append(media[0])

	    elif 'id' in postvars:
		for track_id in postvars['id']:
		    self.db.select('filename')
		    self.db.where('id', track_id)
		    self.db.order_by('filename ASC')
		    for media in self.db.get('media'):
			files.append(media[0])

	    if 'pl_replace' in postvars:
		playlist.set_files(files)
	    else:
		playlist.add_files(files)
	return len(files)

    def html_remove_files(self, postvars):
	if 'pl_remove' in postvars and 'media' in postvars:
	    playlist = Playlist(self.current)
	    files = [ ]
	    for media in postvars['media']:
		files.append(urllib.unquote(media))
	    return playlist.remove_files(files)

    def html_add_urls(self, postvars):
	urls = [ ]
	if 'urls' in postvars:
	    for url in postvars['urls']:
		urls.append(urllib.unquote(url))
	    playlist = Playlist(self.current)
	    if 'pl_replace' in postvars:
		playlist.set_files(urls)
	    elif 'pl_enqueue':
		playlist.add_files(urls)
	return len(urls)

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

	if search:
	    self.db.where_like(order, search)

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

    def get_playlist(self, name=None):
	if name is None:
	    name = self.current
	playlist = Playlist(name)
	files = playlist.get_files()
	return files

    def sort_playlist(self, name=None):
	if name is None:
	    name = self.current
	playlist = Playlist(name)
	files = playlist.get_files()
	if files is  None:
	    return 0
	files.sort()
	return playlist.set_files(files)

    def shuffle_playlist(self, name=None):
	if name is None:
	    name = self.current
	playlist = Playlist(name)
	files = playlist.get_files()
	if files is  None:
	    return 0
	random.shuffle(files)
	return playlist.set_files(files)

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


class MediaUpdaterTask (nerve.Task):
    def __init__(self, medialib, path):
	nerve.Task.__init__(self, 'MediaUpdaterTask')
	self.medialib = medialib
	self.db = nerve.DatabaseCursor(self.medialib.dbconnection)
	self.path = path

    def hash_file(self, filename):
	(mode, inode, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)

	safe_filename = filename
	if isinstance(filename, unicode):
	    safe_filename = filename.encode('utf-8', 'replace')

	rows = list(self.db.get('media', 'id,file_last_modified', self.db.inline_expr('filename', filename)))
	if len(rows) > 0 and mtime <= rows[0][1]:
	    nerve.log("Skipping " + safe_filename)
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

    def run(self):
	for libpath in self.path:
	    for root, dirs, files in os.walk(unicode(libpath)):
		if self.stopflag.isSet():
		    return
		nerve.log("Searching " + root)
		for media in files:
		    if media.endswith('.mp3'):
			self.hash_file(os.path.join(root, media))


class MetaData (object):
    def __init__(self, filename):
	self.filename = filename
	self.meta = { }
	try:
	    self.meta = mutagen.File(filename, None, True)
	except ValueError:
	    pass

    def get(self, name, default=None):
	if self.meta and name in self.meta and len(self.meta[name]) > 0:
	    return self.meta[name][0].encode('utf-8', 'replace')
	return default



class YoutubePlaylistFetcher (nerve.Task):
    def __init__(self, medialib, list_ids):
	nerve.Task.__init__(self, 'YoutubePlaylistFetcher')
	self.list_ids = list_ids
	self.medialib = medialib

	self.db = nerve.DatabaseCursor(self.medialib.dbconnection)
	self.json = None

    def hash_video(self, meta):
	url = 'http://www.youtube.com/watch?v=%s' % (meta['encrypted_id'],)

	rows = list(self.db.get('media', 'id,file_last_modified', self.db.inline_expr('filename', url)))
	if len(rows) > 0 and rows[0][1] >= meta['time_created']:
	    nerve.log("Skipping " + url)
	    return url

	parts = meta['title'].split("-", 1)
	if len(parts) < 2:
	    artist = meta['author']
	    title = meta['title']
	else:
	    artist = parts[0].strip()
	    title = parts[1].strip()
	data = {
	    'filename' : url,
	    'artist' : artist,
	    'title' : title,
	    'album' : 'YouTube',
	    'track_num' : '',
	    'genre' : '',
	    'tags' : meta['keywords'],
	    'media_type' : 'video',
	    'duration' : meta['length_seconds'],
	    'file_size' : '',
	    'file_last_modified' : meta['time_created'],
	}

	if len(rows) <= 0:
	    nerve.log("Adding " + url)
	    self.db.insert('media', data)
	else:
	    nerve.log(u"Updating " + url)
	    self.db.where('id', rows[0][0])
	    self.db.update('media', data)
	return url

    def fetch_json(self, list_id):
	url = 'http://www.youtube.com/list_ajax?action_get_list=1&style=json&list=%s' % (list_id,)
	r = requests.get(url)
	if r.text:
	    return json.loads(r.text)
	return None

    def run(self):
	for list_id in self.list_ids:
	    data = self.fetch_json(list_id)
	    if data is None or 'video' not in data:
		nerve.log("Unable to fetch youtube playlist " + list_id)
	    else:
		playlist = [ ]
		for video in data['video']:
		    if self.stopflag.isSet():
			return
		    url = self.hash_video(video)
		    playlist.append(url)
		pl = Playlist(data['title'])
		pl.set_files(playlist)


