#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

import sys
import os.path
import traceback

import urllib
import urllib.parse

from .models import PagesModel


class PagesController (nerve.http.Controller):
    def __init__(self, **config):
        super().__init__(**config)
        self.model = PagesModel()

    def do_request(self, request):
        page = request.next_segment()
        if not page:
            page = 'index'

        if hasattr(self, page):
            func = getattr(self, page)
            func(request)

        else:
            data = self.model.render_page(page)
            if not data:
                raise nerve.NotFoundError("Page not found: " + page)
            data['pagename'] = page
            self.load_view('nerve/pages/views/template.pyhtml', data)

    def handle_error(self, error, traceback):
        if type(error) == nerve.NotFoundError or self.get_mimetype() != None:
            super().handle_error(error, traceback)
        else:
            self.write_json({ 'status' : 'error', 'message' : error.args[0] })

    def listpages(self, request):
        data = { }
        data['pages'] = self.model.list_pages()
        #self.load_view('nerve/pages/views/listpages.pyhtml', data)

        sectiondata = self.model.render_page(None)
        sectiondata['sidebar'] += self.load_view_as_string('nerve/pages/views/blk-sidebar.pyhtml', data)
        sectiondata['content'] = self.load_view_as_string('nerve/pages/views/blk-listpages.pyhtml', data)
        self.load_view('nerve/pages/views/template.pyhtml', sectiondata)

    def editpage(self, request):
        data = { }
        data['pagename'] = request.next_segment(default='')

        if request.segments_left() > 0:
            raise nerve.ControllerError("Too many path segments given")
        if data['pagename'] and not self.model.page_exists(data['pagename']):
            raise nerve.NotFoundError("Page doesn't exist: " + data['pagename'])

        data['sections'] = self.model.get_page_sections()
        data['pagedata'] = self.model.get_page_data(data['pagename']) if data['pagename'] else ''
        data['blocklist'] = self.model.list_blocks()
        #self.load_view('nerve/pages/views/editpage.pyhtml', data)

        sectiondata = self.model.render_page(None)
        sectiondata['sidebar'] += self.load_view_as_string('nerve/pages/views/blk-sidebar.pyhtml', data)
        sectiondata['content'] = self.load_view_as_string('nerve/pages/views/blk-editpage.pyhtml', data)
        self.load_view('nerve/pages/views/template.pyhtml', sectiondata)

    def savepage(self, request):
        originalname = request.arg('originalname')
        pagename = request.arg('pagename')

        if not pagename:
            raise nerve.ControllerError('You must provide a name for this page')
        if originalname and not self.model.page_exists(originalname):
            raise nerve.ControllerError('Attempting to save non-existent page: ' + originalname)
        if not originalname and self.model.page_exists(pagename):
            raise nerve.ControllerError('A page by that name already exists: ' + pagename)

        pagedata = { }
        for (name, title, typename) in self.model.get_page_sections():
            if typename == 'text':
                pagedata[name] = request.arg(name, default="")
            elif typename.startswith('list:'):
                pagedata[name] = [ item.strip() for item in request.arg(name, default="").split(',') if item ]

        self.model.save_page_data(originalname, pagename, pagedata)
        self.write_json({ 'status' : 'success', 'message' : 'Page saved successfully' })

    def deletepage(self, request):
        pagename = request.arg('name', default=None)

        if not pagename:
            raise nerve.ControllerError('You must provide a page name to delete')
        if not self.model.page_exists(pagename):
            raise nerve.ControllerError('Attempting to delete non-existent page: ' + pagename)

        self.model.delete_page(pagename)
        self.write_json({ 'status' : 'success', 'message' : 'Page deleted successfully' })

    def listblocks(self, request):
        data = { }
        data['blocks'] = self.model.list_blocks()
        #self.load_view('nerve/pages/views/listblocks.pyhtml', data)

        sectiondata = self.model.render_page(None)
        sectiondata['sidebar'] += self.load_view_as_string('nerve/pages/views/blk-sidebar.pyhtml', data)
        sectiondata['content'] = self.load_view_as_string('nerve/pages/views/blk-listblocks.pyhtml', data)
        self.load_view('nerve/pages/views/template.pyhtml', sectiondata)

    def editblock(self, request):
        data = { }
        data['blockname'] = request.next_segment(default='')

        if request.segments_left() > 0:
            raise nerve.ControllerError("Too many path segments given")
        if data['blockname'] and not self.model.block_exists(data['blockname']):
            raise nerve.ControllerError("Block doesn't exist: " + data['blockname'])

        data['blocktext'] = self.model.get_block(data['blockname']) if data['blockname'] else ''
        #self.load_view('nerve/pages/views/editblock.pyhtml', data)

        sectiondata = self.model.render_page(None)
        sectiondata['sidebar'] += self.load_view_as_string('nerve/pages/views/blk-sidebar.pyhtml', data)
        sectiondata['content'] = self.load_view_as_string('nerve/pages/views/blk-editblock.pyhtml', data)
        self.load_view('nerve/pages/views/template.pyhtml', sectiondata)

    def saveblock(self, request):
        originalname = request.arg('originalname')
        blockname = request.arg('blockname')
        blocktext = request.arg('blocktext')

        if not blockname:
            raise nerve.ControllerError('You must provide a name for this block')
        if originalname and not self.model.block_exists(originalname):
            raise nerve.ControllerError('Attempting to save non-existent block: ' + originalname)
        if not originalname and self.model.block_exists(blockname):
            raise nerve.ControllerError('A block by that name already exists: ' + blockname)

        self.model.save_block(originalname, blockname, blocktext)
        self.write_json({ 'status' : 'success', 'message' : 'Block saved successfully' })

    def deleteblock(self, request):
        blockname = request.arg('name', default=None)

        if not blockname:
            raise nerve.ControllerError('You must provide a block name to delete')
        if not self.model.block_exists(blockname):
            raise nerve.ControllerError('Attempting to delete non-existent block: ' + blockname)

        self.model.delete_block(blockname)
        self.write_json({ 'status' : 'success', 'message' : 'Block deleted successfully' })


