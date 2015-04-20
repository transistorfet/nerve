#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

import os.path


class Controller (nerve.Controller):
    def __init__(self, **config):
        nerve.Controller.__init__(self, **config)
        self.header_bytes = None
        self.footer_bytes = None
        self.css_files = [ ]
        self.js_files = [ ]

    def load_view(self, filename, data=None):
        self.set_mimetype('text/html')
        engine = nerve.http.PyHTML(filename, None, data)
        contents = engine.evaluate()
        self.write_text(contents)

    def load_header(self, filename, data=None):
        engine = PyHTML(filename, None, data)
        self.header_bytes = bytes(engine.evaluate(), 'utf-8')

    def load_footer(self, filename, data=None):
        engine = PyHTML(filename, None, data)
        self.footer_bytes = bytes(engine.evaluate(), 'utf-8')

    def add_css(self, filename):
        self.css_files.append(filename)

    def add_js(self, filename):
        self.js_files.append(filename)

    def get_output(self):
        output = nerve.Controller.get_output(self)
        if self.mimetype == 'text/html':
            if self.header_bytes:
                output = self.header_bytes + output
            if self.footer_bytes:
                output = output + self.footer_bytes
        return output

    def assets(self, request):
        filename = 'nerve' + request.url.path

        if '/../' in filename or not os.path.isfile(filename):
            self.write_text("Error file not found: " + filename)
            raise Exception("Error file not found: " + filename)

        (_, _, extension) = filename.rpartition('.')

        if extension == 'pyhtml':
            self.set_mimetype('text/html')
            engine = nerve.http.PyHTML(filename, request)
            contents = engine.evaluate()
            self.write_text(contents)
        else:
            self.write_file(filename)


