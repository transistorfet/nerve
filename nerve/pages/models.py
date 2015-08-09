#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import json


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


class PagesModel (nerve.Model):
    def __init__(self, **config):
        super().__init__(**config)
        self.db = nerve.Database('pages.sqlite')
        self.db.create_table('blocks', "id INTEGER PRIMARY KEY, name TEXT, creator TEXT, data TEXT")
        self.db.create_table('pages', "id INTEGER PRIMARY KEY, name TEXT, creator TEXT, data TEXT")

    def list_blocks(self):
        self.db.select("id, name")
        self.db.order_by('name')
        return list(self.db.get('blocks'))

    def block_exists(self, name):
        self.db.where('name', name)
        results = list(self.db.get('blocks'))
        if len(results) <= 0:
            return False
        return True

    def get_block(self, name):
        self.db.select("name, data")
        self.db.where('name', name)
        results = list(self.db.get('blocks'))
        if len(results) <= 0:
            return None
        return results[0][1]

    def save_block(self, original, name, text):
        data = { 'name': name, 'data': text }
        if original:
            self.db.where('name', original)
            self.db.update('blocks', data)
        else:
            self.db.insert('blocks', data)

    def delete_block(self, name):
        self.db.where('name', name)
        self.db.delete('blocks')

    def get_page_sections(self):
        return page_sections.copy()

    def list_pages(self):
        self.db.select("id, name")
        self.db.order_by('name')
        return list(self.db.get('pages'))

    def page_exists(self, name):
        self.db.where('name', name)
        results = list(self.db.get('pages'))
        if len(results) <= 0:
            return False
        return True

    def get_page_data(self, name):
        self.db.select("name, data")
        self.db.where('name', name)
        results = list(self.db.get('pages'))
        if len(results) <= 0:
            return None
        return json.loads(results[0][1])

    def save_page_data(self, original, name, data):
        data = { 'name': name, 'data': json.dumps(data) }
        if original:
            self.db.where('name', original)
            self.db.update('pages', data)
        else:
            self.db.insert('pages', data)

    def delete_page(self, name):
        self.db.where('name', name)
        self.db.delete('pages')

    # TODO should this function be here, or should there be a View class that actually renders the page using the model for data?
    def render_page(self, name):
        defaultpage = self.get_page_data('__default__')
        if name:
            pagedata = self.get_page_data(name)
            if pagedata is None:
                return None
        else:
            pagedata = None

        page = { }
        for (name, title, typename) in page_sections:
            if typename == 'text':
                if pagedata and name in pagedata:
                    page[name] = pagedata[name]
                elif defaultpage and name in defaultpage:
                    page[name] = defaultpage[name]
                else:
                    page[name] = ''

            elif typename.startswith('list:'):
                itemlist = []
                if defaultpage and name in defaultpage:
                    itemlist += defaultpage[name]
                if pagedata and name in pagedata:
                    itemlist += pagedata[name]

                if typename == 'list:blocks':
                    html = ""
                    for blockname in itemlist:
                        blockdata = self.get_block(blockname)
                        if blockdata:
                            html += blockdata
                        html += '\n'
                    page[name] = html

                else:
                    page[name] = itemlist

        return page



