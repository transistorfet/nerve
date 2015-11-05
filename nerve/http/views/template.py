#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http


class TemplateView (nerve.View):
    def __init__(self, filename=None, data=dict(), **config):
        super().__init__(**config)
        self._mimetype = 'text/html'
        self._filename = filename if filename else 'nerve/http/views/template.tpl.pyhtml'
        self._data = data
        self._sections = self._config.copy()  #self.get_config_info().get_defaults()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('title', "Page Title", default='')
        config_info.add_setting('theme', "Theme Name", default='default')
        config_info.add_setting('separator', "Separator", datatype='textarea', default="<hr/>\n")
        config_info.add_setting('jsfiles', "JavaScript Files", default=list(), itemtype='str')
        config_info.add_setting('cssfiles', "CSS Files", default=list(), itemtype='str')
        config_info.add_setting('header', "Header", default=list(), itemtype='view')
        config_info.add_setting('subheader', "Sub-Header", default=list(), itemtype='view')
        config_info.add_setting('sidebar', "Sidebar", default=list(), itemtype='view')
        config_info.add_setting('content', "Content", default=list(), itemtype='view')
        config_info.add_setting('footer', "Footer", default=list(), itemtype='view')
        config_info.add_setting('subfooter', "Sub-Footer", default=list(), itemtype='view')
        return config_info

    def add_to_section(self, name, view):
        if type(self._sections[name]) == list:
            self._sections[name].append(view)
        else:
            self._sections[name] = view

    def render(self):
        for (section, items) in self._sections.items():
            if type(self._sections[section]) == list:
                self._data[section] = [ str(value) for value in items ]
            else:
                self._data[section] = str(self._sections[section])

        contents = nerve.http.PyHTML(None, self._data, self._filename).get_output()
        self.write_bytes(contents)



