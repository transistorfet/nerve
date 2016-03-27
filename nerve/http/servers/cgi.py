#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import cgi
import urllib.parse


class CGIHandler (nerve.Server):
    def do_request(self, environ=os.environ):
        #print('Content-Type: text/html')
        #print()
        #for (key, value) in sorted(environ.items()):
        #    print(key, value)

        reqtype = environ['REQUEST_METHOD']
        scheme = environ['REQUEST_SCHEME']
        servername = environ['SERVER_NAME']
        path = environ['REQUEST_URI']
        uri = urllib.parse.urlunsplit( (scheme, servername, path, '', '') )
        postvars = cgi.parse(environ=environ)

        headers = { }
        for (key, value) in environ.items():
            if key.startswith('HTTP_'):
                name = key[5:].lower().replace('_', '-')
                headers[name] = value

        request = nerve.Request(self, None, reqtype, uri, postvars, headers=headers)
        controller = self.make_controller(request)
        controller.handle_request(request)

        redirect = controller.get_redirect()
        error = controller.get_error()
        headers = controller.get_headers()
        mimetype = controller.get_mimetype()
        output = controller.get_output()

        if redirect:
            self.send_content(302, mimetype, output, [ ('Location', redirect) ] + headers)
        elif error:
            if type(error) == nerve.users.UserPermissionsRequired:
                self.send_401(str(error))
            else:
                self.send_content(404 if type(error) is nerve.NotFoundError else 500, mimetype, output, headers)
        else:
            self.send_content(200, mimetype, output, headers)
        return

    def send_400(self):
        self.send_content(400, 'text/plain', '400 Bad Request')

    def send_401(self, message):
        self.send_content(401, 'text/html', message, [ ('WWW-Authenticate', 'Basic realm="Secure Area"') ])

    def send_404(self):
        self.send_content(404, 'text/plain', '404 Not Found')

    def send_content(self, errcode, mimetype, content, headers=None):
        if isinstance(content, str):
            content = bytes(content, 'utf-8')
        #self.send_response(errcode)
        if content:
            self.send_header('Content-Type', mimetype)
            self.send_header('Content-Length', len(content))
        else:
            self.send_header('Content-Length', 0)
        if headers:
            for (header, value) in headers:
                self.send_header(header, value)
        self.end_headers()
        if content:
            self.send_data(content)

    def send_header(self, name, value):
        print("{0}: {1}".format(name, value))

    def end_headers(self):
        print()

    def send_data(self, content):
        print(content.decode('utf-8'))
 
