#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

from ..models import PagesModel
from ..views.block import BlockView


page_sections = [
    ('title', "Page Title", 'text'),
    ('jsfiles', "JavaScript Files", 'list:files:js'),
    ('cssfiles', "CSS Files", 'list:files:css'),
    ('header', "Header", 'list:blocks'),
    ('subheader', "Sub-Header", 'list:blocks'),
    ('sidebar', "Sidebar", 'list:blocks'),
    ('content', "Content", 'list:blocks'),
    ('separator', "Separator", 'list:blocks'),
    ('footer', "Footer", 'list:blocks'),
    ('subfooter', "Sub-Footer", 'list:blocks')
]

class PageView (nerve.http.TemplateView):
    def __init__(self, pagename=None, data=dict()):
        super().__init__('nerve/pages/views/template.pyhtml', data)
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

        for (name, title, typename) in page_sections:
            if typename == 'text':
                if pagedata and name in pagedata:
                    self._sections[name] = pagedata[name]
                elif defaultpage and name in defaultpage:
                    self._sections[name] = defaultpage[name]
                else:
                    self._sections[name] = ''

            elif typename.startswith('list:'):
                itemlist = []
                if defaultpage and name in defaultpage:
                    itemlist += defaultpage[name]
                if pagedata and name in pagedata:
                    itemlist += pagedata[name]

                if typename == 'list:blocks':
                    for blockname in itemlist:
                        self.add_to_section(name, BlockView(blockname))
                else:
                    for item in itemlist:
                        self.add_to_section(name, item)

        super().render()

    @staticmethod
    def get_page_sections():
        return page_sections.copy()


 
