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
from .views.page import PageView


class PagesController (nerve.http.Controller):
    def __init__(self, **config):
        super().__init__(**config)
        self.model = PagesModel()

    def do_request(self, request):
        page = request.next_segment()
        if not page:
            page = 'index'

        if hasattr(self, page):
            method = getattr(self, page)
            if not nerve.is_public(method):
                raise nerve.users.UserPermissionsError("method is not public: " + name)
            method(request)

        elif self.model.page_exists(page):
            template = self.get_setting('template')
            if not template and request:
                template = request.source.get_setting('template')
            template = template.copy()

            data = { }
            data['pagename'] = page
            self.set_view(PageView(page, data, **template))
            #self.template_add_to_section('jsfiles', '/pages/assets/js/pages.js')
            self.template_add_to_section('cssfiles', '/pages/assets/css/pages.css')

        else:
            raise nerve.NotFoundError("Page not found: " + page)

    @nerve.public
    def listpages(self, request):
        data = { }
        data['pages'] = self.model.list_pages()

        self.load_template_view('nerve/pages/views/editor/listpages.blk.pyhtml', data, request)
        self.template_add_to_section('sidebar', self.make_html_view('nerve/pages/views/editor/sidebar.blk.pyhtml', data))
        self.template_add_to_section('jsfiles', '/pages/assets/js/pages.js')
        self.template_add_to_section('cssfiles', '/pages/assets/css/pages.css')

    @nerve.public
    def editpage(self, request):
        data = { }
        data['pagename'] = request.next_segment(default='')

        if request.segments_left() > 0:
            raise nerve.ControllerError("Too many path segments given")
        if data['pagename'] and not self.model.page_exists(data['pagename']):
            raise nerve.NotFoundError("Page doesn't exist: " + data['pagename'])

        data['sections'] = PageView.get_config_info()
        data['pagedata'] = self.model.get_page_data(data['pagename']) if data['pagename'] else None

        data['sections'].add_setting('originalname', "", default=data['pagename'], datatype='hidden', weight=-11)
        data['sections'].add_setting('pagename', "Page Name", default=data['pagename'], weight=-10)

        #self.load_template_view('nerve/pages/views/editor/editpage.blk.pyhtml', data, request)
        self.load_template_view(None, data, request)
        self.template_add_to_section('sidebar', self.make_html_view('nerve/pages/views/editor/sidebar.blk.pyhtml', data))
        self.template_add_to_section('content', nerve.base.FormView(data['sections'], data['pagedata'], target='/pages/savepage', title="Edit Page", textbefore='<div id="page-editor">', textafter='</div>'))
        self.template_add_to_section('jsfiles', '/assets/js/formview.js')
        self.template_add_to_section('jsfiles', '/pages/assets/js/pages.js')
        self.template_add_to_section('cssfiles', '/pages/assets/css/pages.css')

    @nerve.public
    def savepage(self, request):
        originalname = request.arg('originalname')
        pagename = request.arg('pagename')

        if not pagename:
            raise nerve.ControllerError('You must provide a name for this page')
        if originalname and not self.model.page_exists(originalname):
            raise nerve.ControllerError('Attempting to save non-existent page: ' + originalname)
        if not originalname and self.model.page_exists(pagename):
            raise nerve.ControllerError('A page by that name already exists: ' + pagename)

        pagedata = PageView.get_config_info().validate(request.args)

        self.model.save_page_data(originalname, pagename, pagedata)
        self.load_json_view({ 'status' : 'success', 'message' : 'Page saved successfully' })

    @nerve.public
    def deletepage(self, request):
        pagename = request.arg('name', default=None)

        if not pagename:
            raise nerve.ControllerError('You must provide a page name to delete')
        if not self.model.page_exists(pagename):
            raise nerve.ControllerError('Attempting to delete non-existent page: ' + pagename)

        self.model.delete_page(pagename)
        self.load_json_view({ 'status' : 'success', 'message' : 'Page deleted successfully' })

    @nerve.public
    def listblocks(self, request):
        data = { }
        data['blocks'] = self.model.list_blocks()
        self.load_template_view('nerve/pages/views/editor/listblocks.blk.pyhtml', data, request)
        self.template_add_to_section('sidebar', self.make_html_view('nerve/pages/views/editor/sidebar.blk.pyhtml', data))
        self.template_add_to_section('jsfiles', '/pages/assets/js/pages.js')
        self.template_add_to_section('cssfiles', '/pages/assets/css/pages.css')

    @nerve.public
    def editblock(self, request):
        data = { }
        data['blockname'] = request.next_segment(default='')

        if request.segments_left() > 0:
            raise nerve.ControllerError("Too many path segments given")
        if data['blockname'] and not self.model.block_exists(data['blockname']):
            raise nerve.ControllerError("Block doesn't exist: " + data['blockname'])

        data['blocktext'] = self.model.get_block(data['blockname']) if data['blockname'] else ''

        self.load_template_view('nerve/pages/views/editor/editblock.blk.pyhtml', data, request)
        self.template_add_to_section('sidebar', self.make_html_view('nerve/pages/views/editor/sidebar.blk.pyhtml', data))
        self.template_add_to_section('jsfiles', '/pages/assets/js/pages.js')
        self.template_add_to_section('cssfiles', '/pages/assets/css/pages.css')

    @nerve.public
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
        self.load_json_view({ 'status' : 'success', 'message' : 'Block saved successfully' })

    @nerve.public
    def deleteblock(self, request):
        blockname = request.arg('name', default=None)

        if not blockname:
            raise nerve.ControllerError('You must provide a block name to delete')
        if not self.model.block_exists(blockname):
            raise nerve.ControllerError('Attempting to delete non-existent block: ' + blockname)

        self.model.delete_block(blockname)
        self.load_json_view({ 'status' : 'success', 'message' : 'Block deleted successfully' })

    def handle_error(self, error, traceback, request):
        if request.reqtype == 'POST' and type(error) is not nerve.users.UserPermissionsRequired:
            self.load_json_view({ 'status' : 'error', 'message' : error.args[0] })
        else:
            super().handle_error(error, traceback, request)


