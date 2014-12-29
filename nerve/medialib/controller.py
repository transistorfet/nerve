# -*- coding: utf-8 -*-
#!/usr/bin/python

import nerve
import nerve.http
import nerve.medialib

import urllib
import urlparse


class MediaLibController (nerve.http.Controller):

    def index(self, request):
	medialib = nerve.get_device('medialib')

	data = { }
	data['list_of_playlists'] = medialib.get_playlist_list()
	self.load_view('nerve/medialib/views/index.pyhtml', data)

    def get_playlist(self, request):
	medialib = nerve.get_device('medialib')
	playlist = request.args['playlist'][0] if 'playlist' in request.args else 'default'

	data = { }
	data['playlist'] = medialib.get_playlist(playlist)
	self.load_view('nerve/medialib/views/playlist.pyhtml', data)

    def search(self, request):
	medialib = nerve.get_device('medialib')

	data = { }
	data['list_of_playlists'] = medialib.get_playlist_list()
	data['mode'] = request.arg('mode', default='album')
	data['order'] = request.arg('order', default='artist')
	data['offset'] = request.arg('offset', default=0)
	data['limit'] = request.arg('limit', default=1000)
	data['search'] = request.arg('search', default='%')
	data['recent'] = request.arg('recent', default=None)
	data['media_type'] = request.arg('type', default=None)

	self.load_view('nerve/medialib/views/search.pyhtml', data)

    def get_search_results(self, request):
	medialib = nerve.get_device('medialib')

	mode = request.arg('mode')
	order = request.arg('order')
	offset = request.arg('offset', default=0)
	limit = request.arg('limit', default=1000)
	search = request.arg('search', default='')
	recent = request.arg('recent', default='')
	media_type = request.arg('type', default='')

	data = { }
	data['media_list'] = medialib.get_media_list(mode, order, offset, limit, search, recent, media_type)
	data['mode'] = mode
	self.load_view('nerve/medialib/views/search-results.pyhtml', data)

    def shuffle_playlist(self, request):
	medialib = nerve.get_device('medialib')
	playlist = request.args['playlist'][0]
	medialib.shuffle_playlist(playlist)

    def sort_playlist(self, request):
	medialib = nerve.get_device('medialib')
	playlist = request.args['playlist'][0]
	medialib.sort_playlist(playlist)

    def add_tracks(self, request):
	medialib = nerve.get_device('medialib')
	result = dict(count=0)
	media = [ ]
	if 'method' in request.args and 'playlist' in request.args and 'media[]' in request.args:
	    for argstr in request.args['media[]']:
		query = urlparse.parse_qs(argstr)
		media.extend(medialib.get_media_query(query))
	    playlist = nerve.medialib.Playlist(request.arg('playlist'))
	    if request.arg('method') == 'replace':
		result['count'] = playlist.set_list(media)
	    elif request.arg('method') == 'enqueue':
		result['count'] = playlist.add_list(media)
	self.write_json(result)

    def add_urls(self, request):
	result = dict(count=0)
	urls = [ ]
	if 'playlist' in request.args and 'urls[]' in request.args:
	    for url in request.args['urls[]']:
		urls.append(urllib.unquote(url))
	    playlist = nerve.medialib.Playlist(request.args['playlist'])
	    if 'pl_replace' in request.args:
		result['count'] = playlist.set_files(urls)
	    elif 'pl_enqueue':
		result['count'] = playlist.add_files(urls)
	self.write_json(result)

    def remove_urls(self, request):
	result = dict(count=0)
	urls = [ ]
	if 'playlist' in request.args and 'urls[]' in request.args:
	    for url in request.args['urls[]']:
		urls.append(urllib.unquote(url))
	    playlist = nerve.medialib.Playlist(request.args['playlist'][0])
	    result['count'] = playlist.remove_files(urls)
	self.write_json(result)


