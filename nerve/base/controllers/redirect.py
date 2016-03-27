#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
from nerve.http import PyHTML

import os.path
import mimetypes

class RedirectController (nerve.Controller):

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('redirect', "Redirect", default='')
        return config_info

    def do_request(self, request):
        path = self.get_setting('redirect').rstrip('/')
        slug = request.get_slug().rstrip('/')
        if slug:
            path += '/' + slug
        self.redirect_to(path)


