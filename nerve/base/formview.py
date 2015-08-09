#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import io


class FormView (nerve.View):
    def __init__(self, config_info):
        self._output = io.StringIO()
        self._config_info = config_info
        self._last_label = 0

    def get_output(self):
        self.build_form()
        return self._output.getvalue()

    def build_form(self):
        self._output.write('<div class="nerve-treeview">\n')

        for item in self._config_info:
            self.build_item(self, item)

        self._output.write('</div>\n')

    def build_item(self, item):
        if item['datatype'] in ('dict', 'list'):
            self.build_complex_item(item)
        else:
            self.build_scalar_item(item)

    def build_scalar_item(self, item):
        self._output.write('<li><div class="nerve-form-item">\n')
        self._output.write('    <label>' + item['propername'] + '</label>\n')
        self._output.write('    <span><input type="text" name="' + item['name'] + '" value="' + obj[name] + '" /></span>\n')
        self._output.write('</div></li>\n')

    def build_complex_item(self, item):
        self._last_label += 1
        subitems = item['iteminfo']

        self._output.write('<li><input type="checkbox" id="item-' + str(self._last_label) + '" /><label class="nerve-treeview alt-label" for="item-' + str(self._last_label) + '">' + objname + '</label>\n')
        self._output.write('<ul>\n')

        for subitem in subitems:
            self.build_item(subitem)

        self._output.write('</ul></li>\n')


