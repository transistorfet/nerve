#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http
import nerve.medialib

import urllib
import urllib.parse

import json
import requests

class MediaLibController (nerve.http.Controller):

    def index(self, request):
        medialib = nerve.get_object('/devices/medialib')

        data = { }
        data['list_of_playlists'] = medialib.get_playlist_list()
        self.load_view('nerve/medialib/views/playlist.pyhtml', data)

    def get_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist = request.args['playlist'] if 'playlist' in request.args else 'default'

        data = { }
        data['playlist'] = medialib.get_playlist(playlist)
        self.load_view('nerve/medialib/views/playlist-data.pyhtml', data)

    def search(self, request):
        medialib = nerve.get_object('/devices/medialib')

        data = { }
        data['list_of_playlists'] = medialib.get_playlist_list()
        data['mode'] = request.arg('mode', default='album')
        data['order'] = request.arg('order', default='artist')
        data['offset'] = request.arg('offset', default=0)
        data['limit'] = request.arg('limit', default=1000)
        data['search'] = request.arg('search', default='')
        data['recent'] = request.arg('recent', default=None)
        data['media_type'] = request.arg('media_type', default=None)

        if request.arg('mode'):
            data['media_list'] = medialib.get_media_list(data['mode'], data['order'], data['offset'], data['limit'], data['search'], data['recent'], data['media_type'])
        else:
            data['media_list'] = None

        self.load_view('nerve/medialib/views/search.pyhtml', data)

    def search_youtube(self, request):
        medialib = nerve.get_object('/devices/medialib')

        data = { }
        data['list_of_playlists'] = medialib.get_playlist_list()
        data['media_list'] = None
        data['search'] = request.arg('search', default='')

        if data['search']:
            url = "http://ajax.googleapis.com/ajax/services/search/video?v=1.0&rsz=large&q=%s" % (data['search'],)
            r = requests.get(url)
            if r.text:
                data['media_list'] = json.loads(r.text)
                #print(json.dumps(data['media_list'], sort_keys=True, indent=4, separators=(',', ':')))

        self.load_view('nerve/medialib/views/search_youtube.pyhtml', data)

    def shuffle_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist = request.args['playlist']
        medialib.shuffle_playlist(playlist)

    def sort_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist = request.args['playlist']
        medialib.sort_playlist(playlist)

    def create_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist_name = request.args['playlist']
        for name in medialib.get_playlist_list():
            if name == playlist_name:
                self.write_json({ 'error' : "A playlist by that name already exists" })
                return
        playlist = nerve.medialib.Playlist.create(playlist_name)
        self.write_json({ 'notice' : "Playlist created successfully" })

    def delete_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist_name = request.args['playlist']
        for name in medialib.get_playlist_list():
            if name == playlist_name:
                self.write_json({ 'notice' : "Playlist deleted successfully" })
                nerve.medialib.Playlist.delete(playlist_name)
                return
        self.write_json({ 'error' : "That playlist no longer exists" })

    def add_tracks(self, request):
        medialib = nerve.get_object('/devices/medialib')
        result = dict(count=0)
        media = [ ]
        if 'method' in request.args and 'playlist' in request.args and 'media[]' in request.args:
            for argstr in request.args['media[]']:
                query = urllib.parse.parse_qs(argstr)
                media.extend(medialib.get_media_query(query))
            if request.arg('method') == 'playnow':
                player = nerve.get_object('/devices/player')
                if len(media) > 0:
                    player.play(media[0]['filename'])
                    for media_item in media[1:]:
                        player.enqueue(media_item['filename'])
                result['count'] = len(media)
            else:
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
                urls.append(urllib.parse.unquote(url))
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
                urls.append(urllib.parse.unquote(url))
            playlist = nerve.medialib.Playlist(request.args['playlist'])
            result['count'] = playlist.remove_files(urls)
        self.write_json(result)

    def rehash_database(self, request):
        medialib = nerve.get_object('/devices/medialib')
        medialib.force_database_update()


