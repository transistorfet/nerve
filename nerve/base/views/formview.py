#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import cgi
import urllib.parse


def pathjoin(base, name):
    return base + '/' + name if base else name


class FormView (nerve.View):
    # TODO change config_info to type, so any type can have a form
    def __init__(self, data, config_info):
        super().__init__()
        self._data = data
        self._config_info = config_info
        self._indent = 2
        self._last_label = 0

    def write_text(self, text):
        super().write_text(('    ' * self._indent) + text)

    def render(self):
        self.build_form()

    def build_form(self):
        self.write_text('<div class="nerve-treeview">\n')
        self._indent += 1
        self.build_complex_item('', '', '', self._config_info, self._data)
        self._indent -= 1
        self.write_text('<br/>\n')
        self.write_text('<button class="nerve-form-submit">Save</button>\n')
        self.write_text('</div>\n')

    def build_item(self, basename, name, propername, datatype, data):
        if datatype.is_type('scalar'):
            self.build_scalar_item(basename, name, propername, datatype, data)
        else:
            self._last_label += 1
            if datatype.is_type('object'):
                self.write_text('<li><input type="checkbox" id="item-' + str(self._last_label) + '" /><label class="nerve-treeview" for="item-' + str(self._last_label) + '">' + pathjoin(basename, propername) + '</label>\n')
            else:
                self.write_text('<li><input type="checkbox" id="item-' + str(self._last_label) + '" checked /><label class="nerve-treeview alt-label" for="item-' + str(self._last_label) + '">' + propername + '</label>\n')
            self.build_complex_item(basename, name, propername, datatype, data)
            self.write_text('</li>\n')

    def build_scalar_item(self, basename, name, propername, datatype, data):
        self.write_text('<li><div class="nerve-form-item">\n')
        self.write_text('    <label>' + propername + '</label>\n')
        """
        if 'options' in setting and setting['options']:
            self.write_text('    <span><select name="' + pathjoin(basename, name) + '">\n')
            for (propername, value) in setting['options']:
                self.write_text('<option value="' + cgi.escape(str(value)) + '">' + propername + '</option>\n')
            self.write_text('    </select></span>\n')
        """
        if datatype.htmltype == 'textarea':
            self.write_text('    <span><textarea name="' + pathjoin(basename, name) + '">' + cgi.escape(str(data)) + '</textarea></span>\n')
        else:
            #urllib.parse.quote(str(itemvalue))
            self.write_text('    <span><input type="' + datatype.htmltype + '" name="' + pathjoin(basename, name) + '" value="' + cgi.escape(str(data)) + '" /></span>\n')
        self.write_text('</div></li>\n')

    def build_complex_item(self, basename, name, propername, datatype, data):

        self.write_text('<ul class="nerve-form-tree" name="' + pathjoin(basename, name) + '">\n')
        self._indent += 1

        for (itemname, itempropername, itemdatatype, itemdata) in datatype.get_items(data):
            self.build_item(pathjoin(basename, name), itemname, itempropername, itemdatatype, itemdata)

        self.write_text('<button class="nerve-config-add" data-object="dirname">Add</button>\n')

        """
                <button class="add" data-object="<%= dirname %>">Add</button>
                <div style="display: none;">
                    <div id="nerve-notice" style="display: none;"></div>
                    <div id="nerve-error" style="display: none;"></div>
                    <div class="nerve-form-item-row">
                        <input type="text" name="__name__" />
                        <select class="add-select-type">
                            <option value="">(select type)</option>
                            <% for typename in typeslist: %>
                            <option value="<%= typename %>"><%= typename %></option>
                            <% end %>
                        </select>
                    </div>
                    <div id="add-settings"></div>
                    <div>
                        <button class="add-create" data-object="<%= dirname %>">Create</button>
                        <button class="add-cancel">Cancel</button>
                    </div>
                </div>
        """


        self._indent -= 1
        self.write_text('</ul>\n')


