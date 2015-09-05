#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

import os.path
import hashlib
import http.cookies


class Controller (nerve.Controller):
    def __init__(self, **config):
        super().__init__(**config)

    def make_html_view(self, filename, data=None, request=None):
        return nerve.http.PyHTML(request, data, filename)

    def load_html_view(self, filename, data=None, request=None):
        self.set_view(nerve.http.PyHTML(request, data, filename))

    def load_template_view(self, filename=None, data=None, request=None, template_data=dict()):
        template = self.get_setting('template')
        if not template and request:
            template = request.source.get_setting('template')
        if not template:
            template = { '__type__': 'http/views/template/TemplateView', 'filename': 'nerve/http/views/template.pyhtml' }
        template = template.copy()

        template_class = nerve.Module.get_class(template['__type__'])
        del template['__type__']
        view = template_class(**template)
        if filename:
            view.add_to_section('content', nerve.http.PyHTML(request, data, filename))
        self.set_view(view)

    def template_add_to_section(self, name, view):
        self._view.add_to_section(name, view)

    @nerve.public
    def assets(self, request):
        filename = 'nerve' + request.url.path

        if '/../' in filename or not os.path.isfile(filename):
            raise nerve.NotFoundError("Error file not found: " + filename)

        (_, _, extension) = filename.rpartition('.')
        if extension == 'pyhtml':
            self.set_view(nerve.http.PyHTML(request, None, filename))
        else:
            self.load_file_view(filename)


class SessionMixIn (object):
    """Add cookie-based sessions to a Controller"""
    _sessions = { }

    def initialize(self, request):
        self.cookie = http.cookies.SimpleCookie('\n'.join(request.get_header_all("cookie")))
        if 'SESSIONID' in self.cookie:
            self.sessionid = self.cookie['SESSIONID'].value
        else:
            self.sessionid = hashlib.sha512(os.urandom(64)).hexdigest()

        if self.sessionid not in SessionMixIn._sessions:
            SessionMixIn._sessions[self.sessionid] = { }
        self.session = SessionMixIn._sessions[self.sessionid]
        print("Init: ", self.sessionid, self.session)
        super().initialize(request)

    def finalize(self, request):
        super().finalize(request)
        print("Final: ", self.sessionid, self.session)
        SessionMixIn._sessions[self.sessionid] = self.session
        self.cookie['SESSIONID'] = self.sessionid
        print(self.cookie)
        for morsel in self.cookie.values():
            self.add_header('Set-Cookie', morsel.output(header=''))


