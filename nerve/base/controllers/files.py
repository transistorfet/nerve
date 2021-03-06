#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
from nerve.http import PyHTML

import os.path
import mimetypes

class FileController (nerve.Controller):

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('root', "Root Directory", default='nerve/http/wwwdata')
        return config_info

    def do_request(self, request):
        filename = nerve.files.find_source(os.path.join(self.get_setting('root'), request.get_slug()))

        if not nerve.files.validate(filename):
            raise Exception("invalid path: " + repr(filename))

        if os.path.isdir(filename):
            filename = os.path.join(filename, "index.html")

        if not os.path.isfile(filename):
            raise nerve.NotFoundError("Error file not found: " + filename)

        (_, _, extension) = filename.rpartition('.')
        if extension == 'pyhtml':
            self.set_view(PyHTML(request, None, filename))
        else:
            self.load_file_view(filename) 

