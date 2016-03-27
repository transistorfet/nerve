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
        data['limit'] = request.arg('limit', default=0)
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
    def add_media_items(self, request):
        operation = request.arg('operation')
        if not operation:
            raise nerve.ControllerError("'operation' field must be set")
        if not request.arg('media[]'):
            raise nerve.ControllerError("'media[]' field must be set")

        count = 0
        medialib = nerve.get_object('/devices/medialib')

        media = [ ]
        for argstr in request.arg('media[]'):
            query = urllib.parse.parse_qs(argstr)
            media.extend(medialib.get_media_query(query))

        if operation == 'playnow':
            player = nerve.get_object('/devices/player')
            if len(media) > 0:
                player.play(media[0]['filename'])
                for media_item in media[1:]:
                    player.enqueue(media_item['filename'])
            count = len(media)

        elif operation in [ 'enqueue', 'replace' ]:
            if not request.arg('playlist'):
                raise nerve.ControllerError("'playlist' field must be set")
            playlist = nerve.medialib.Playlist(request.arg('playlist'))
            if operation == 'replace':
                count = playlist.set_list(media)
            elif operation == 'enqueue':
                count = playlist.add_list(media)

        if count > 0:
            self.load_json_view({ 'notice': str(count) + " track(s) were added to playlist " + request.arg('playlist') })
        else:
            self.load_json_view({ 'error': "No tracks were added" })

    @nerve.public
    def add_urls(self, request):
        urls = [ ]
        if 'playlist' in request.args and 'urls[]' in request.args:
            for url in request.args['urls[]']:
                urls.append(urllib.parse.unquote(url))
            playlist = nerve.medialib.Playlist(request.args['playlist'])
            if 'pl_replace' in request.args:
                count = playlist.set_files(urls)
            elif 'pl_enqueue':
                count = playlist.add_files(urls)

        if count > 0:
            self.load_json_view({ 'notice': str(count) + " track(s) were added to playlist " + request.arg('playlist') })
        else:
            self.load_json_view({ 'error': "No tracks were added" })

    @nerve.public
    def remove_urls(self, request):
        urls = [ ]
        if 'playlist' in request.args and 'urls[]' in request.args:
            for url in request.args['urls[]']:
                urls.append(urllib.parse.unquote(url))
            playlist = nerve.medialib.Playlist(request.args['playlist'])
            count = playlist.remove_files(urls)

        if count > 0:
            self.load_json_view({ 'notice': str(count) + " track(s) were removed from playlist " + request.arg('playlist') })
        else:
            self.load_json_view({ 'error': "No tracks were removed" })

    @nerve.public
    def modify_tags(self, request):
        medialib = nerve.get_object('/devices/medialib')

        if not request.arg('media[]'):
            raise nerve.ControllerError("'media[]' field must be set")

        if not request.arg('tags'):
            raise nerve.ControllerError("'tags' field must be set")
        tags = nerve.medialib.MediaLibDevice.split_tags(request.arg('tags'))

        media = [ ]
        for argstr in request.arg('media[]'):
            query = urllib.parse.parse_qs(argstr)
            media.extend(medialib.get_media_query(query))

        for media_item in media:
            for tag in tags:
                if tag[0] != '!':
                    medialib.add_tag(media_item['id'], tag)
                else:
                    medialib.remove_tag(media_item['id'], tag[1:])

        if len(media) > 0:
            self.load_json_view({ 'notice': str(len(media)) + " track(s) tags modified" })
        else:
            self.load_json_view({ 'error': "No tags were modified" })

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
        self.load_json_view({ 'notice': "Tags added" })

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
        self.load_json_view({ 'notice': "Tags removed" })

    @nerve.public
    def rehash(self, request):
        medialib = nerve.get_object('/devices/medialib')
        medialib.rehash()

        accept = request.get_header('accept')
        if 'application/json' in accept:
            self.load_json_view({ 'notice': "Rehashing database..." })
        elif 'text/html' in accept:
            self.load_template_view(None, { }, request)
            self.template_add_to_section('content', '<h4>Rehashing database...</h4>')



