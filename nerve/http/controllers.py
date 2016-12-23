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

    def initialize(self, request):
        super().initialize(request)
        self._cookie = http.cookies.SimpleCookie('\n'.join(request.get_header_all("cookie")))
        self._set_cookie = http.cookies.SimpleCookie()

    def finalize(self, request):
        for morsel in self._set_cookie.values():
            self.add_header('Set-Cookie', morsel.output(header='').lstrip())
        super().finalize(request)

    def set_cookie(self, name, value, domain=None, path=None, expires=None, secure=False):
        self._set_cookie[name] = value
        if domain:
            self._set_cookie[name]['domain'] = domain
        if path:
            self._set_cookie[name]['path'] = path
        if expires:
            self._set_cookie[name]['expires'] = expires
        if secure is True:
            self._set_cookie[name]['secure'] = True

    def make_html_view(self, filename, data=None, request=None):
        return nerve.http.PyHTML(request, data, filename)

    def load_html_view(self, filename, data=None, request=None):
        self.set_view(nerve.http.PyHTML(request, data, filename))

    def find_template(self, request=None):
        template = self.get_setting('template')

        if not template:
            if not request:
                request = self.get_request()
            if request and request.source:
                template = request.source.get_setting('template')

        if not template:
            template = { '__type__': 'http/views/template/TemplateView' }

        return template.copy()

    def load_template_view(self, filename=None, data=None, request=None, template_data=dict()):
        template = self.find_template(request)

        template_class = nerve.modules.get_class(template['__type__'])
        del template['__type__']
        view = template_class(data=template_data, **template)
        if filename:
            view.add_to_section('content', nerve.http.PyHTML(request, data, filename))
        self.set_view(view)

    def template_add_to_section(self, name, view):
        self._view.add_to_section(name, view)

    @nerve.public
    def assets(self, request):
        if not nerve.files.validate(request.url.path):
            raise Exception("invalid path: " + repr(filename))
        filename = nerve.files.find_source('nerve/' + request.url.path.lstrip('/'))

        if not os.path.isfile(filename):
            raise nerve.NotFoundError("Error file not found: " + filename)

        (_, _, extension) = filename.rpartition('.')
        if extension == 'pyhtml':
            self.set_view(nerve.http.PyHTML(request, None, filename))
        else:
            self.load_file_view(filename)

    def handle_error(self, error, traceback, request):
        accept = request.get_header('accept', default='text/html')
        if 'application/json' in accept and type(error) is not nerve.users.UserPermissionsRequired:
            nerve.log(traceback, logtype='error')
            self.load_json_view({ 'error' : repr(error) })
        else:
            super().handle_error(error, traceback, request)


class SessionMixIn (object):
    """Add cookie-based sessions to a Controller object"""
    _sessions = { }

    def initialize(self, request):
        super().initialize(request)
        if 'SESSIONID' in self._cookie:
            self.sessionid = self._cookie['SESSIONID'].value
        else:
            self.sessionid = nerve.users.random_token() #hashlib.sha512(os.urandom(64)).hexdigest()
            self.set_cookie('SESSIONID', self.sessionid, path='/')

        if self.sessionid not in SessionMixIn._sessions:
            SessionMixIn._sessions[self.sessionid] = { }
        self.session = SessionMixIn._sessions[self.sessionid]
        # TODO automatically log user in?
        if '__LOGIN_TOKEN__' in self.session:
            nerve.users.login_token(self.session['__LOGIN_TOKEN__'])

    def finalize(self, request):
        SessionMixIn._sessions[self.sessionid] = self.session
        super().finalize(request)

    def handle_error(self, error, traceback, request):
        # TODO also check that the user isn't already logged in.  If so, display an error
        if type(error) == nerve.users.UserPermissionsRequired:
            # TODO can we make this a setting somehow??
            self.redirect_to('/users/login')
        else:
            super().handle_error(error, traceback, request)


class SessionController (SessionMixIn, Controller):
    pass


