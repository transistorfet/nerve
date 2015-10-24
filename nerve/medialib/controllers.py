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

    @nerve.public
    def index(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist = request.args['playlist'] if 'playlist' in request.args else 'default'

        data = { }
        data['list_of_playlists'] = medialib.get_playlist_list()
        self.load_template_view('nerve/medialib/views/playlist.blk.pyhtml', data, request)
        self.template_add_to_section('jsfiles', '/medialib/assets/js/medialib.js')
        self.template_add_to_section('cssfiles', '/medialib/assets/css/medialib.css')

    @nerve.public
    def get_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist = request.args['playlist'] if 'playlist' in request.args else 'default'

        data = { }
        data['playlist'] = medialib.get_playlist(playlist)
        try:
            data['current_pos'] = nerve.query('/devices/player/get_position')
        except:
            data['current_pos'] = 0
        self.load_html_view('nerve/medialib/views/playlist-data.blk.pyhtml', data)

    @nerve.public
    def search(self, request):
        medialib = nerve.get_object('/devices/medialib')

        data = { }
        data['medialib'] = medialib
        data['list_of_playlists'] = medialib.get_playlist_list()
        data['mode'] = request.arg('mode', default='album')
        data['order'] = request.arg('order', default='artist')
        data['offset'] = request.arg('offset', default=0)
        data['limit'] = request.arg('limit', default=1000)
        data['search'] = request.arg('search', default='')
        data['tags'] = request.arg('tags', default='')
        data['recent'] = request.arg('recent', default=None)
        data['media_type'] = request.arg('media_type', default=None)

        if request.arg('mode'):
            data['media_list'] = medialib.get_media_list(data['mode'], data['order'], data['offset'], data['limit'], data['search'], data['recent'], data['media_type'], data['tags'])
        else:
            data['media_list'] = None

        self.load_template_view('nerve/medialib/views/search.blk.pyhtml', data, request)
        self.template_add_to_section('jsfiles', '/medialib/assets/js/medialib.js')
        self.template_add_to_section('cssfiles', '/medialib/assets/css/medialib.css')

    @nerve.public
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

        self.load_template_view('nerve/medialib/views/search_youtube.blk.pyhtml', data, request)
        self.template_add_to_section('jsfiles', '/medialib/assets/js/medialib.js')
        self.template_add_to_section('cssfiles', '/medialib/assets/css/medialib.css')

    @nerve.public
    def shuffle_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist = request.args['playlist']
        medialib.shuffle_playlist(playlist)

    @nerve.public
    def sort_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist = request.args['playlist']
        medialib.sort_playlist(playlist)

    @nerve.public
    def create_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist_name = request.args['playlist']
        for name in medialib.get_playlist_list():
            if name == playlist_name:
                raise nerve.ControllerError("A playlist by that name already exists")

        playlist = nerve.medialib.Playlist.create(playlist_name)
        self.load_json_view({ 'notice' : "Playlist created successfully" })

    @nerve.public
    def delete_playlist(self, request):
        medialib = nerve.get_object('/devices/medialib')
        playlist_name = request.args['playlist']
        for name in medialib.get_playlist_list():
            if name == playlist_name:
                nerve.medialib.Playlist.delete(playlist_name)
                self.load_json_view({ 'notice' : "Playlist deleted successfully" })
                return
        self.load_json_view({ 'error' : "That playlist no longer exists" })

    @nerve.public
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
            elif request.arg('method') == 'markwatched':
                for media_item in media:
                    medialib.add_tag(media_item['id'], 'watched')
            else:
                playlist = nerve.medialib.Playlist(request.arg('playlist'))
                if request.arg('method') == 'replace':
                    result['count'] = playlist.set_list(media)
                elif request.arg('method') == 'enqueue':
                    result['count'] = playlist.add_list(media)
        self.load_json_view(result)

    @nerve.public
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
        self.load_json_view(result)

    @nerve.public
    def remove_urls(self, request):
        result = dict(count=0)
        urls = [ ]
        if 'playlist' in request.args and 'urls[]' in request.args:
            for url in request.args['urls[]']:
                urls.append(urllib.parse.unquote(url))
            playlist = nerve.medialib.Playlist(request.args['playlist'])
            result['count'] = playlist.remove_files(urls)
        self.load_json_view(result)

    @nerve.public
    def add_tag(self, request):
        medialib = nerve.get_object('/devices/medialib')
        id = request.arg('id')
        tag = request.arg('tag')
        if tag.startswith('"'):
            tag = tag[1:]
        if tag.endswith('"'):
            tag = tag[:-1]
        medialib.add_tag(id, tag)
        self.load_json_view({ 'status': 'success' })

    @nerve.public
    def remove_tag(self, request):
        medialib = nerve.get_object('/devices/medialib')
        id = request.arg('id')
        tag = request.arg('tag')
        if tag.startswith('"'):
            tag = tag[1:]
        if tag.endswith('"'):
            tag = tag[:-1]
        medialib.remove_tag(id, tag)
        self.load_json_view({ 'status': 'success' })

    @nerve.public
    def rehash_database(self, request):
        medialib = nerve.get_object('/devices/medialib')
        medialib.force_database_update()

    def handle_error(self, error, traceback, request):
        if request.reqtype == 'POST' and type(error) is not nerve.users.UserPermissionsRequired:
            self.load_json_view({ 'error' : repr(error) })
        else:
            super().handle_error(error, traceback, request)


