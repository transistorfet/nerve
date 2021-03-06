#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve 
import nerve.http

from ..views.formview import FormView


class ConfigController (nerve.http.Controller):

    @nerve.public
    def index(self, request):
        nerve.users.require_group('admin')
        # TODO can you for this path without refering directly to the module (ie. using what's in the request)
        self.load_template_view('nerve/base/views/config/settings.blk.pyhtml', { }, request)
        self.template_add_to_section('jsfiles', '/assets/js/formview.js')

    """
    @nerve.public
    def test(self, request):
        obj = nerve.get_object("/")
        self.load_template_view(None, None, request)
        self.template_add_to_section('jsfiles', '/assets/js/formview.js')
        self.template_add_to_section('content', FormView(nerve.types.ObjectConfigType(), obj.get_config_data(), action='/config/save'))
        #self.template_add_to_section('content', FormView(obj.get_config_info(), obj.get_config_data()))
        #self.template_add_to_section('content', FormView(nerve.http.views.template.TemplateView.get_config_info(), self._view._sections))

    @nerve.public
    def test2(self, request):
        self.load_template_view('nerve/base/views/tabstest.blk.pyhtml', None, request)
        self.template_add_to_section('jsfiles', '/assets/js/formview.js')

    @nerve.public
    def set_theme(self, request):
        name = request.arg('name')
        self.add_header('Set-Cookie', 'theme=' + name + '; Domain=' + request.get_host())
    """




    @nerve.public
    def add(self, request):
        nerve.users.require_group('admin')

        path = request.get_slug()
        if not path:
            raise nerve.ControllerError("You must provide a valid object name")

        #self.set_view(FormView(nerve.types.ConfigType.get_type('object'), { '__type__': request.arg('type') }))

        form = FormView(nerve.types.ConfigType.get_type('object'), None, '/config/create/' + path + '/new', submitname="Create", submitback=True)

        if request.arg('dialog'):
            self.set_view(form)
        else:
            self.load_template_view(None, None, request)
            self.template_add_to_section('jsfiles', '/assets/js/formview.js')
            self.template_add_to_section('content', form)


    @nerve.public
    def create(self, request):
        nerve.users.require_group('admin')

        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        path = request.get_slug()
        if not path:
            raise nerve.ControllerError("You must provide a valid object name")
        (dirname, _, name) = path.rpartition('/')
        typeinfo = request.arg('__type__')

        if not dirname or not nerve.has_object(dirname):
            raise nerve.ControllerError("The directory you've specified is invalid.")
        if not name:
            raise nerve.ControllerError("You must provide a valid name.")
        if nerve.has_object(dirname + '/' + name):
            raise nerve.ControllerError("An object of that name already exists.")
        if not typeinfo:
            raise nerve.ControllerError("You must select a type.")

        defaults = nerve.ObjectNode.get_class_config_info(typeinfo)
        config = defaults.validate(request.args)

        obj = nerve.ObjectNode.make_object(typeinfo, config)
        nerve.set_object(dirname + '/' + name, obj)
        nerve.save_config()
        self.load_json_view({ 'notice': "Object created" })


    @nerve.public
    def edit(self, request):
        nerve.users.require_group('admin')

        path = request.get_slug()
        if not path:
            raise nerve.ControllerError("You must provide a valid object name")

        obj = nerve.get_object(path)
        if not obj:
            raise nerve.ControllerError("Object not found: " + path)

        form = FormView(obj.get_config_info(), obj.get_config_data(), '/config/save/' + path, submitback=True)

        if request.arg('dialog'):
            self.set_view(form)
        else:
            self.load_template_view(None, None, request)
            self.template_add_to_section('jsfiles', '/assets/js/formview.js')
            self.template_add_to_section('content', form)


    @nerve.public
    def defaults(self, request):
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)
        if not request.arg('type'):
            raise nerve.ControllerError("You must select a type first")

        basename = request.arg('basename', default='')
        self.set_view(FormView(nerve.types.ConfigType.get_type('object'), { '__type__': request.arg('type') }, basename=basename))


    @nerve.public
    def save(self, request):
        nerve.users.require_group('admin')

        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        path = request.get_slug()
        if not path:
            raise nerve.ControllerError("You must provide a valid object name")

        print(path)
        print(request.args)

        obj = nerve.get_object(path)
        config = obj.get_config_info().validate(request.args)
        obj.update_config_data(config)

        nerve.save_config()
        self.load_json_view({ 'notice': "Saved successfully" })


    @nerve.public
    def rename(self, request):
        nerve.users.require_group('admin')

        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        # TODO you totally don't validate these names enough
        oldname = request.arg('oldname')
        newname = request.arg('newname')

        if not oldname or not nerve.has_object(oldname):
            raise nerve.ControllerError("The directory you've specified is invalid.")
        if not newname:
            raise nerve.ControllerError("The new name given is invalid.")
        if nerve.has_object(newname):
            raise nerve.ControllerError("An object of that name already exists.")

        obj = nerve.get_object(oldname)
        if not nerve.del_object(oldname):
            raise nerve.ControllerError("Unable to rename this object.")
        nerve.set_object(newname, obj)

        nerve.save_config()
        self.load_json_view({ 'notice': "Object renamed" })


    @nerve.public
    def delete(self, request):
        nerve.users.require_group('admin')

        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        objectname = request.args['objectname']
        if not objectname or not nerve.has_object(objectname):
            raise nerve.ControllerError("The object you've specified doesn't exist.")

        result = nerve.del_object(objectname)
        if not result:
            raise nerve.ControllerError("Unable to delete object.")

        nerve.save_config()
        self.load_json_view({ 'notice': "Object deleted" })



