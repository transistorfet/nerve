#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

import os.path


class Controller (nerve.Controller):
    def __init__(self, **config):
        super().__init__(**config)
        self.header_bytes = None
        self.footer_bytes = None
        self.css_files = [ ]
        self.js_files = [ ]

    def load_view_as_string(self, filename, data=None):
        contents = nerve.http.PyHTML(None, data, filename).evaluate()
        return contents

    def load_view(self, filename, data=None):
        self.set_mimetype('text/html')
        contents = nerve.http.PyHTML(None, data, filename).evaluate()
        self.write_text(contents)

    def load_header(self, filename, data=None):
        engine = PyHTML(None, data, filename)
        self.header_bytes = bytes(engine.evaluate(), 'utf-8')

    def load_footer(self, filename, data=None):
        engine = PyHTML(None, data, filename)
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
            raise nerve.NotFoundException("Error file not found: " + filename)

        (_, _, extension) = filename.rpartition('.')

        if extension == 'pyhtml':
            self.set_mimetype('text/html')
            contents = nerve.http.PyHTML(request, None, filename).evaluate()
            self.write_text(contents)
        else:
            self.write_file(filename)


