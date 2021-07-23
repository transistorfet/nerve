#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import html
import random
import urllib.parse


class FormView (nerve.HTMLView):
    # TODO change config_info to type, so any type can have a form
    def __init__(self, config_info, data, action=None, formid=None, basename='', submitname='Save', submitback=False, title=None, textbefore=None, textafter=None):
        super().__init__()
        self._data = data
        self._config_info = config_info
        self._action = action
        self._formid = formid
        self._basename = basename
        self._submitname = submitname
        self._submitback = submitback
        self._title = title
        self._textbefore = textbefore
        self._textafter = textafter
        self._last_label = 0

    def render(self):
        self.build_form()

    def build_form(self):
        idattr = ' id="' + str(self._formid) + '"' if self._formid else ''
        actionattr = ' action="' + str(self._action) + '"' if self._action else ''
        backattr = ' data-back="true"' if self._submitback else ''

        self.write('<form{0} class="nerve-form" method="post"{1}{2}>\n'.format(idattr, actionattr, backattr), tab=1)
        if self._textbefore:
            self.write(self._textbefore + '\n')
        if self._title:
            self.write('<h4>{0}</h4>\n'.format(self._title))
        self.build_complex_item('', self._basename, '', self._config_info, self._data)
        if self._action:
            self.write('<br/>\n')
            self.write('<button type="submit" class="nerve-form-submit">{0}</button>\n'.format(self._submitname))
        if self._textafter:
            self.write(self._textafter + '\n')
        self.write('</form>\n', tab=-1)

    def build_item(self, basename, name, propername, datatype, data, parenttype=None):
        self.write('<li name="{0}">\n'.format(nerve.join_path(basename, name)), tab=1)
        if datatype.is_type('scalar'):
            self.build_scalar_item(basename, name, propername, datatype, data)
        else:
            alt_label = ' alt-label' if not datatype.is_type('object') else ''
            expand_label = 'e' + str(random.randint(0, 65536)) + "-" + nerve.join_path(basename, name)
            self.write('<input type="checkbox" id="{0}" checked />\n'.format(expand_label))
            self.write('<label class="nerve-form-tree{0}" for="{1}"><span>{2}</span></label>\n'.format(alt_label, expand_label, propername))
            self.build_complex_item(basename, name, propername, datatype, data)
        self.build_container_item_buttons(parenttype)
        self.write('</li>\n', tab=-1)

    def build_scalar_item(self, basename, name, propername, datatype, data):
        formatted_data = html.escape(datatype.render(data), True)

        if datatype.htmltype == 'hidden':
            self.write('<div class="nerve-form-item" style="display: none;"><input type="hidden" name="{0}" value="{1}" /></div>\n'.format(nerve.join_path(basename, name), formatted_data))
            return

        self.write('<div class="nerve-form-item">\n', tab=1)
        self.write('<label>{0}</label>\n'.format(propername))

        options = datatype.get_options()
        if options:
            self.write('<span><select name="{0}"{1}>\n'.format(nerve.join_path(basename, name), ' class="nerve-form-change-type"' if datatype.is_type('object-type') else ''))
            for (propername, value) in options:
                self.write('<option value="{0}"{1}>{2}</option>\n'.format(html.escape(str(value)), ' selected' if value == data else '', propername))
            self.write('</select></span>\n')

        elif datatype.htmltype == 'textarea':
            self.write('<span><textarea name="{0}">{1}</textarea></span>\n'.format(nerve.join_path(basename, name), formatted_data))

        elif datatype.htmltype == 'checkbox':
            self.write('<span><input type="checkbox" name="{0}" {1}/></span>\n'.format(nerve.join_path(basename, name), 'checked' if data else ''))

        else:
            self.write('<span><input type="{0}" name="{1}" value="{2}" /></span>\n'.format(datatype.htmltype, nerve.join_path(basename, name), formatted_data))

        self.write('</div>\n', tab=-1)

    def build_complex_item(self, basename, name, propername, datatype, data):
        self.write('<ul class="nerve-form-tree{0}" name="{1}">\n'.format(' list' if datatype.is_type('list') else '', nerve.join_path(basename, name)), tab=1)

        for (itemname, itempropername, itemdatatype, itemdata) in datatype.get_items(data):
            self.build_item(nerve.join_path(basename, name), itemname, itempropername, itemdatatype, itemdata, datatype)

        if datatype.is_type('container'):
            self.write('<button class="nerve-form-add" data-name="{0}">Add</button>\n'.format(nerve.join_path(basename, name)))
            self.write('<div style="display: none;">\n', tab=1)
            self.build_item(nerve.join_path(basename, name), '__new__', "__new__", datatype.itemtype, None, datatype)
            self.write('</div>\n', tab=-1)

        self.write('</ul>\n', tab=-1)

    def build_container_item_buttons(self, parenttype):
        if parenttype and parenttype.is_type('container'):
            self.write('<div class="nerve-form-buttons">\n', tab=1)
            if parenttype.is_type('list'):
                self.write('<button class="nerve-form-move-up">&#9651;</button>\n')
                self.write('<button class="nerve-form-move-down">&#9661;</button>\n')
            else:
                self.write('<button class="nerve-form-rename">Rename</button>\n')
            self.write('<button class="nerve-form-delete">Delete</button>\n')
            self.write('</div>\n', tab=-1)


