# -*- coding: utf-8 -*-
#!/usr/bin/python

import nerve

import apsw
import time
import os
import os.path
import mutagen

import urllib
import codecs
import random

import requests
import json

class Database (object):
    def __init__(self, filename):
	self.filename = filename
	self.dbcon = apsw.Connection(os.path.join(nerve.configdir(), filename))


class DatabaseCursor (object):
    def __init__(self, db):
	self.db = db
	self.dbcursor = self.db.dbcon.cursor()
	self.reset_cache()

    def reset_cache(self):
	self.cache_where = u""
	self.cache_group = u""
	self.cache_order = u""
	self.cache_limit = u""
	self.cache_select = u"*"
	self.cache_distinct = u""

    def query(self, q):
	self.dbcursor.execute(text)

    def table_exists(self, name):
        for row in self.dbcursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name = '" + name + "' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table','view') AND name = '" + name + "'"):
            return True
        return False

    def create_table(self, table, columns):
	self.dbcursor.execute(u"CREATE TABLE IF NOT EXISTS %s (%s)" % (table, columns))

    def escape(self, text):
	if text is None:
	    return u""
	if isinstance(text, str):
	    text = unicode(text, 'utf-8')
	elif not isinstance(text, unicode):
	    text = str(text)
	return text.replace(u"'", u"''")

    def inline_expr(self, name, val, compare='='):
	return u"%s%s'%s' " % (name, compare, self.escape(val))

    def where(self, where, val, compare='='):
	where_sql = self.inline_expr(where, val, compare)
	if not self.cache_where:
	    self.cache_where = where_sql
	else:
	    self.cache_where += u" AND " + where_sql

    def where_not(self, where, val):
	self.where(where, val, "<>")

    def where_gt(self, where, val):
	self.where(where, val, ">")

    def where_lt(self, where, val):
	self.where(where, val, "<")

    def where_like(self, where, val):
	self.where(where, val, " LIKE ")

    def set_where(self, where):
	self.cache_where = where

    def group_by(self, group):
	self.cache_group = group

    def order_by(self, order):
	self.cache_order = order

    def limit(self, limit):
	self.cache_limit = limit

    def select(self, fields):
	self.cache_select = fields

    def distinct(self, enabled):
	if enabled is True:
	    self.cache_distinct = u'DISTINCT'
	else:
	    self.cache_distinct = u""

    def compile_clauses(self):
	query = u""
	if self.cache_where:
	    query += u"WHERE %s " % (self.cache_where,)
	if self.cache_group:
	    query += u"GROUP BY %s " % (self.cache_group,)
	if self.cache_order:
	    query += u"ORDER BY %s " % (self.cache_order,)
	if self.cache_limit:
	    query += u"LIMIT %s " % (self.cache_limit,)
	return query

    def compile_select(self, table, select=None, where=None):
	if select is not None:
	    self.cache_select = select
	if where is not None:
	    self.cache_where = where

	query = u"SELECT %s %s FROM %s " % (self.cache_distinct, self.cache_select, table)
	query += self.compile_clauses()
	return query

    def get(self, table, select=None, where=None):
	query = self.compile_select(table, select, where)
	#print query
	result = self.dbcursor.execute(query)
	#result = self.dbcursor.execute(query.decode('utf-8'))
	self.reset_cache()
	return result

    def get_assoc(self, table, select=None, where=None):
	query = self.compile_select(table, select, where)
	#print query.encode('utf-8', 'replace')
	result = self.dbcursor.execute(query)
	#result = self.dbcursor.execute(query.decode('utf-8'))

	# TODO this doesn't work with SELECT *
	keys = [ key.strip() for key in self.cache_select.split(',') ]
	rows = [ ]
	for row in result:
	    assoc = { }
	    for i in range(len(keys)):
		if isinstance(row[i], unicode):
		    assoc[keys[i]] = row[i].encode('utf-8')
		else:
		    assoc[keys[i]] = row[i]
	    rows.append(assoc)

	self.reset_cache()
	return rows

    def insert(self, table, data):
	columns = data.keys()
	values = [ ]
	for key in columns:
	    values.append(u"\'%s\'" % (self.escape(data[key]),))

	query = u"INSERT INTO %s (%s) VALUES (%s)" % (table, ','.join(columns), ','.join(values))
	#print query
	self.dbcursor.execute(query)
	#self.dbcursor.execute(query.decode('utf-8'))
	self.reset_cache()

    def update(self, table, data, where=None):
	if where is not None:
	    self.cache_where = where

	values = [ ]
	for key in data.keys():
	    values.append(u"%s=\'%s\'" % (key, self.escape(data[key])))

	query = u"UPDATE %s SET %s " % (table, ','.join(values))
	query += self.compile_clauses()
	#print query
	result = self.dbcursor.execute(query)
	#result = self.dbcursor.execute(query.decode('utf-8'))
	self.reset_cache()
	return result

    """
    def select(self, table, values=None, where=None, whereval=None, order_by=None):
	if values is None:
	    values = '*'
	query = "SELECT %s FROM %s " % (values, table)
	if where is not None:
	    query += "WHERE %s='%s' " % (where, self.escape(whereval))
	if order_by is not None:
	    query += "ORDER BY %s " % (order_by,)
	return self.dbcursor.execute(query.decode('utf-8'))
    """



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


class Playlist (object):
    def __init__(self, name):
	self.name = name
	plroot = nerve.configdir() + '/playlists'
	if not os.path.isdir(plroot):
	    os.mkdir(plroot)
	self.filename = plroot + '/' + name + '.m3u'

    def get_files(self):
	with codecs.open(self.filename, 'r', encoding='utf-8') as f:
	    contents = f.read().split('\n')
	return contents

    def set_files(self, media_list):
	with codecs.open(self.filename, 'w', encoding='utf-8') as f:
	    for media in media_list:
		f.write(media + '\n')

    def add_files(self, media_list):
	with codecs.open(self.filename, 'a', encoding='utf-8') as f:
	    for media in media_list:
		f.write(media + '\n')

    def remove_files(self, media_list):
	existing_list = self.get_files()
	new_list = [ existing for existing in existing_list if existing not in media_list ]
	self.set_files(new_list)
	return len(existing_list) - len(new_list)

    def clear_playlist(self):
	with codecs.open(self.filename, 'w', encoding='utf-8') as f:
	    f.write('\n')


class YoutubePlaylistFetcher (nerve.Task):
    def __init__(self, list_ids, medialib):
	nerve.Task.__init__(self, 'YoutubePlaylistFetcher')
	self.list_ids = list_ids
	self.medialib = medialib

	self.db = DatabaseCursor(self.medialib.dbconnection)
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


class MediaLib (nerve.Device):
    def __init__(self, path=None):
	nerve.Device.__init__(self)
	#self.path = [ '/media/media/Torrents' ]
	#self.path = [ '/media/media/Music', '/media/media/Torrents' ]
	self.path = [ 'Y:\Torrents', 'Y:\Music' ]
	self.playlists = 'playlists'
	self.current = 'Default'
	self.dbconnection = Database('medialib.sqlite')
	self.db = DatabaseCursor(self.dbconnection)
	self.db.create_table('media', "id INTEGER PRIMARY KEY, filename TEXT, artist TEXT, album TEXT, title TEXT, track_num NUMERIC, genre TEXT, tags TEXT, duration NUMERIC, media_type TEXT, file_hash TEXT, file_size INT, file_last_modified INT")

	# TODO reenable after testing
	#self.thread = MediaUpdaterTask('MediaUpdater', self)
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

    def get_media_list(self, mode, order, offset, limit, search=None, recent=None):
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
    def __init__(self, name, medialib):
	nerve.Task.__init__(self, name)
	self.medialib = medialib
	self.db = DatabaseCursor(self.medialib.dbconnection)

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
	for libpath in self.medialib.path:
	    for root, dirs, files in os.walk(unicode(libpath)):
		if self.stopflag.isSet():
		    return
		nerve.log("Searching " + root)
		for media in files:
		    if media.endswith('.mp3'):
			self.hash_file(os.path.join(root, media))

