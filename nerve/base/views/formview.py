#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import cgi
import urllib.parse


def pathjoin(base, name):
    return base + '/' + name if base else name


class FormView (nerve.View):
    # TODO change config_info to type, so any type can have a form
    def __init__(self, config_info, data, target=None, submit='Save', submitback=False, basename=''):
        super().__init__()
        self._data = data
        self._config_info = config_info
        self._target = target
        self._submit = submit
        self._submitback = submitback
        self._basename = basename
        self._indent = 2
        self._last_label = 0

    def write_text(self, text, indent=0):
        if indent < 0:
            self._indent += indent
        super().write_text(('    ' * self._indent) + text)
        if indent > 0:
            self._indent += indent

    def render(self):
        self.build_form()

    def build_form(self):
        #self.write_text('<div class="nerve-treeview">\n', indent=1)
        self.build_complex_item('', self._basename, '', self._config_info, self._data)
        if self._target:
            self.write_text('<br/>\n')
            self.write_text('<button class="nerve-form-submit" data-target="{0}"{1}>{2}</button>\n'.format(self._target, ' data-back="true"' if self._submitback else '', self._submit))
        #self.write_text('</div>\n', indent=-1)

    def build_item(self, basename, name, propername, datatype, data, parenttype=None):
        self.write_text('<li name={0}>\n'.format(pathjoin(basename, name)), indent=1)
        if datatype.is_type('scalar'):
            self.build_scalar_item(basename, name, propername, datatype, data)
        else:
            alt_label = ' alt-label' if not datatype.is_type('object') else ''
            self.write_text('<input type="checkbox" id="{0}" checked />\n'.format(pathjoin(basename, name)))
            self.write_text('<label class="nerve-form-tree{0}" for="{1}"><span>{2}</span></label>\n'.format(alt_label, pathjoin(basename, name), propername))
            self.build_complex_item(basename, name, propername, datatype, data)
        self.build_container_item_buttons(parenttype)
        self.write_text('</li>\n', indent=-1)

    def build_scalar_item(self, basename, name, propername, datatype, data):
        self.write_text('<div class="nerve-form-item">\n', indent=1)
        self.write_text('<label>{0}</label>\n'.format(propername))

        options = datatype.get_options()
        if options:
            self.write_text('<span><select name="{0}"{1}>\n'.format(pathjoin(basename, name), ' class="nerve-form-change-type"' if datatype.is_type('object-type') else ''))
            for (propername, value) in options:
                self.write_text('<option value="{0}"{1}>{2}</option>\n'.format(cgi.escape(str(value)), ' selected' if value == data else '', propername))
            self.write_text('</select></span>\n')

        elif datatype.htmltype == 'textarea':
            self.write_text('<span><textarea name="{0}">{1}</textarea></span>\n'.format(pathjoin(basename, name), cgi.escape(str(data))))

        elif datatype.htmltype == 'checkbox':
            self.write_text('<span><input type="checkbox" name="{0}" {1}/></span>\n'.format(pathjoin(basename, name), 'checked' if data else ''))

        else:
            #urllib.parse.quote(str(itemvalue))
            self.write_text('<span><input type="{0}" name="{1}" value="{2}" /></span>\n'.format(datatype.htmltype, pathjoin(basename, name), cgi.escape(str(data))))

        self.write_text('</div>\n', indent=-1)

    def build_complex_item(self, basename, name, propername, datatype, data):
        self.write_text('<ul class="nerve-form-tree{0}" name="{1}">\n'.format(' list' if datatype.is_type('list') else '', pathjoin(basename, name)), indent=1)

        for (itemname, itempropername, itemdatatype, itemdata) in datatype.get_items(data):
            self.build_item(pathjoin(basename, name), itemname, itempropername, itemdatatype, itemdata, datatype)

        if datatype.is_type('container'):
            self.write_text('<button class="nerve-form-add" data-name="{0}">Add</button>\n'.format(pathjoin(basename, name)))
            self.write_text('<div style="display: none;">\n', indent=1)
            self.build_item(pathjoin(basename, name), '(new)', "(new)", datatype.itemtype, None, datatype)
            self.write_text('</div>\n', indent=-1)

        self.write_text('</ul>\n', indent=-1)

    def build_container_item_buttons(self, parenttype):
        if parenttype and parenttype.is_type('container'):
            self.write_text('<div class="nerve-form-buttons">\n', indent=1)
            if parenttype.is_type('list'):
                self.write_text('<button class="nerve-form-move-up">Up</button>\n')
                self.write_text('<button class="nerve-form-move-down">Down</button>\n')
            else:
                self.write_text('<button class="nerve-form-rename">Rename</button>\n')
            self.write_text('<button class="nerve-form-delete">Delete</button>\n')
            self.write_text('</div>\n', indent=-1)


