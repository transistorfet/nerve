#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import io


class FormView (nerve.View):
    def __init__(self, config_info, data):
        super().__init__()
        self._config_info = config_info
        self._data = data
        self._last_label = 0

    def finalize(self):
        self.build_form()

    def build_form(self):
        self.write_text('<div class="nerve-treeview">\n')
        self.build_config_item(self._config_info, self._data)
        self.write_text('</div>\n')

    def build_config_item(self, config_info, value):
        for itemconfig in config_info:
            itemvalue = value[itemconfig['name']]
            self.build_item(itemconfig, itemvalue)

    def build_item(self, itemconfig, itemvalue):
        # this would be equiv to itemvalue[item['name']] for a dict or list.  It would be that way for a dict of object settings, but not for an object itself
        #curvalue = item['datatype'].get_value(itemvalue, item['name'])
        #curvalue = data[item['name']]

        if itemconfig['iteminfo'] == None:
            self.build_scalar_item(itemconfig, itemvalue)
        else:
            self.build_complex_item(itemconfig, itemvalue)

    def build_scalar_item(self, itemconfig, itemvalue):
        self.write_text('<li><div class="nerve-form-item">\n')
        self.write_text('    <label>' + itemconfig['propername'] + '</label>\n')
        self.write_text('    <span><input type="text" name="' + itemconfig['name'] + '" value="' + str(itemvalue) + '" /></span>\n')
        self.write_text('</div></li>\n')

    def build_complex_item(self, parentconfig, parentvalue):
        self._last_label += 1

        self.write_text('<li><input type="checkbox" id="item-' + str(self._last_label) + '" /><label class="nerve-treeview alt-label" for="item-' + str(self._last_label) + '">' + parentconfig['name'] + '</label>\n')
        self.write_text('<ul>\n')

        if type(parentconfig['iteminfo']) == nerve.ConfigInfo:
            for (itemkey, itemvalue) in parentconfig['datatype'].get_items(parentvalue):
                self._last_label += 1
                self.write_text('<li><input type="checkbox" id="item-' + str(self._last_label) + '" /><label class="nerve-treeview alt-label" for="item-' + str(self._last_label) + '">' + str(itemkey) + '</label>\n')
                self.write_text('<ul>\n')
                self.build_config_item(parentconfig['iteminfo'], itemvalue)
                self.write_text('</ul></li>\n')
        elif type(parentconfig['iteminfo']) == nerve.ConfigType:
            if parentconfig['iteminfo'].typeclass == 'scalar':
                for (itemkey, itemvalue) in parentconfig['datatype'].get_items(parentvalue):
                    self._last_label += 1
                    self.write_text('<li><label>"' + str(itemkey) + '"</label><input type="text" name="item-' + str(self._last_label) + '" value="' + str(itemvalue) + '"/></li>\n')

        """
        # TODO this is kinda wrong.  It would be the code for a new item in the above list, but not the list itself
        for item in parentconfig['iteminfo']:
            #itemvalue = item['datatype'].get_value(parentvalue, parentconfig['name'])
            itemvalue = parentvalue[item['name']]
            self.build_item(subitem, itemvalue)
        """

        self.write_text('</ul></li>\n')


