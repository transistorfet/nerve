#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import cgi
import traceback
import urllib.parse


class WSGIHandler (nerve.Server):
    def __init__(self, **config):
        super().__init__(**config)

    def __call__(self, environ, start_response):
        #nerve.logs.redirect(environ['wsgi.errors'])

        #for (key, value) in sorted(environ.items()):
        #    print(key, value, file=environ['wsgi.errors'])

        reqtype = environ['REQUEST_METHOD']
        scheme = environ['REQUEST_SCHEME'] if 'REQUEST_SCHEME' in environ else ''
        servername = environ['SERVER_NAME']
        path = environ['PATH_INFO']
        querystring = environ['QUERY_STRING']
        uri = urllib.parse.urlunsplit( (scheme, servername, path, querystring, '') )
        getvars = nerve.core.delistify(cgi.parse_qs(querystring))

        try:
            contentlen = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            contentlen = 0
        contents = environ['wsgi.input'].read(contentlen).decode('utf-8')

        if 'CONTENT_TYPE' in environ:
            (mimetype, pdict) = cgi.parse_header(environ['CONTENT_TYPE'])
        else:
            mimetype = None         # empty post doesn't provide a content-type.

        if mimetype == None:
            postvars = { }
        elif mimetype == 'multipart/form-data':
            postvars = nerve.core.delistify(cgi.parse_multipart(self.rfile, pdict))
        elif mimetype == 'application/x-www-form-urlencoded':
            postvars = nerve.core.delistify(urllib.parse.parse_qs(contents, keep_blank_values=True))
        elif mimetype == 'application/json':
            postvars = json.loads(contents)
        else:
            raise Exception("unrecognized content-type in POST " + self.path + " (" + mimetype + ")")

        postvars.update(getvars)

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
            status = '302 Found'
            headers += [ ('Location', redirect) ]
        elif error:
            if type(error) is nerve.NotFoundError:
                status = '404 Not Found'
            else:
                status = '500 Internal Server Error'
        else:
            status = '200 OK'

        if isinstance(output, str):
            output = bytes(output, 'utf-8')

        if mimetype:
            headers += [ ('Content-Type', mimetype) ]

        if output:
            headers += [ ('Content-Length', str(len(output))) ]
        else:
            headers += [ ('Content-Length', '0') ]

        #print(path, file=environ['wsgi.errors'])
        #for (key, value) in sorted(headers):
        #    print(key, value, file=environ['wsgi.errors'])

        start_response(status, headers)
        #nerve.logs.redirect(None)
        yield output if output is not None else b''

 
