#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

import os.path


class Controller (nerve.Controller):
    def __init__(self, **config):
        super().__init__(**config)

    def load_view_as_string(self, filename, data=None, request=None):
        contents = nerve.http.PyHTML(request, data, filename).get_output()
        return contents

    def load_view(self, filename, data=None, request=None):
        self.set_mimetype('text/html')
        contents = nerve.http.PyHTML(request, data, filename).get_output()
        self.write_text(contents)

    def assets(self, request):
        filename = 'nerve' + request.url.path

        if '/../' in filename or not os.path.isfile(filename):
            raise nerve.NotFoundError("Error file not found: " + filename)

        (_, _, extension) = filename.rpartition('.')

        if extension == 'pyhtml':
            self.set_mimetype('text/html')
            contents = nerve.http.PyHTML(request, None, filename).get_output()
            self.write_text(contents)
        else:
            self.write_file(filename)


