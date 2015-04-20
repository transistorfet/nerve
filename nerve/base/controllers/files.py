#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
from nerve.http import PyHTML

import os.path
import mimetypes

class FileController (nerve.Controller):
    def __init__(self, **config):
        nerve.Controller.__init__(self, **config)

    @staticmethod
    def get_config_info():
        config_info = nerve.Controller.get_config_info()
        config_info.add_setting('root', "Root Directory", default='nerve/http/wwwdata')
        return config_info

    def do_request(self, request):
        filename = os.path.join(self.get_setting('root'), request.remaining_segments())

        if os.path.isdir(filename):
            filename = os.path.join(filename, "index.html")

        if not os.path.isfile(filename):
            self.write_text("Error file not found: " + filename)
            raise Exception("Error file not found: " + filename)

        (_, _, extension) = filename.rpartition('.')

        if extension == 'pyhtml':
            self.set_mimetype('text/html')
            engine = PyHTML(filename, request)
            contents = engine.evaluate()
            self.write_text(contents)
        else:
            self.write_file(filename)


