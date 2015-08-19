#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

import os.path


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

    def assets(self, request):
        filename = 'nerve' + request.url.path

        if '/../' in filename or not os.path.isfile(filename):
            raise nerve.NotFoundError("Error file not found: " + filename)

        (_, _, extension) = filename.rpartition('.')
        if extension == 'pyhtml':
            self.set_view(nerve.http.PyHTML(request, None, filename))
        else:
            self.load_file_view(filename)


