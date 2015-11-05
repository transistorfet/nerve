#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import json


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
        data = { 'name': name, 'data': json.dumps(data, sort_keys=True) }
        if original:
            self.db.where('name', original)
            self.db.update('pages', data)
        else:
            self.db.insert('pages', data)

    def delete_page(self, name):
        self.db.where('name', name)
        self.db.delete('pages')


