#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

from ..models import PagesModel
from ..views.block import BlockView


class PageView (nerve.http.TemplateView):
    def __init__(self, pagename=None, data=dict(), **config):
        super().__init__('nerve/pages/views/template.pyhtml', data, **config)
        self.pagename = pagename
        self.model = PagesModel()

    def render(self):
        defaultpage = self.model.get_page_data('__default__')
        if self.pagename:
            pagedata = self.model.get_page_data(self.pagename)
            if pagedata is None:
                raise Exception("Page data not found: " + self.pagename)
        else:
            pagedata = None

        for (name, propername, datatype, default) in self.get_config_info().get_items(self.get_config_data()):
            if datatype.is_type('scalar'):
                if pagedata and name in pagedata and pagedata[name]:
                    self._sections[name] = pagedata[name]
                elif defaultpage and name in defaultpage and defaultpage[name]:
                    self._sections[name] = defaultpage[name]
                else:
                    self._sections[name] = default

            else:
                itemlist = []
                if defaultpage and name in defaultpage:
                    itemlist += defaultpage[name]
                if pagedata and name in pagedata:
                    itemlist += pagedata[name]

                if datatype.is_type('list:textarea'):
                    for blockname in itemlist:
                        self.add_to_section(name, BlockView(blockname))
                else:
                    for item in itemlist:
                        self.add_to_section(name, item)

        super().render()



 
