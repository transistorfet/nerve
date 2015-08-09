#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve 
import nerve.http

from nerve.base.formview import FormView

class ConfigController (nerve.http.Controller):

    def handle_error(self, error, traceback):
        if type(error) == nerve.ControllerError:
            self.write_json({ 'status' : 'error', 'message' : repr(error) })
        else:
            super().handle_error(error, traceback)

    def index(self, request):
        data = { }
        #self.load_default_data(data)
        # TODO can you for this path without refering directly to the module (ie. using what's in the request)
        #self.load_view("nerve/base/views/config/settings.pyhtml", data)

        #data['formhtml'] = FormView(nerve.main().get_config_info()).get_output()
        self.load_view("nerve/base/views/config/template.pyhtml", data)

    def defaults(self, request):
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unrecognized request type: " + request.reqtype)
        if not request.arg('type'):
            raise nerve.ControllerError("You must select a type first")

        data = { }
        data['config_info'] = nerve.ObjectNode.get_class_config_info(request.arg('type'))
        self.load_view("nerve/base/views/config/blk-configinfo.pyhtml", data)

    def create(self, request):
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unrecognized request type: " + request.reqtype)

        dirname = request.arg('__dir__')
        name = request.arg('__name__')
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
        config = defaults.get_config_info().validate_settings(request.args)

        obj = nerve.ObjectNode.make_object(typeinfo, config)
        nerve.set_object(dirname + '/' + name, obj)
        nerve.save_config()
        self.write_json({ 'status' : 'success' })

    def save(self, request):
        # TODO do authorization check
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unrecognized request type: " + request.reqtype)

        obj = nerve.get_object(request.args['objectname'])
        config = obj.get_config_info().validate_settings(request.args)
        obj.update_config_data(config)

        nerve.save_config()
        self.write_json({ 'status' : 'success' })

    def rename(self, request):
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unrecognized request type: " + request.reqtype)

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
        self.write_json({ 'status' : 'success' })

    def delete(self, request):
        # TODO do authorization check
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unrecognized request type: " + request.reqtype)

        objectname = request.args['objectname']
        if not objectname or not nerve.has_object(objectname):
            raise nerve.ControllerError("The object you've specified doesn't exist.")

        result = nerve.del_object(objectname)
        if not result:
            raise nerve.ControllerError("Unable to delete object.")

        nerve.save_config()
        self.write_json({ 'status' : 'success' })


    # Perhaps save should just write the config file at once, and other operations will manipulate settings without saving them?
    # - need a mechanism to address subsettings... should there still be obj and setting name? combining them would require a way to figure out what part is object vs setting (checking for
    #   object and if not then checking for setting??
    # - there was an idea to use set_setting() instead of set_config_data() but the difference is that the former wont 're-initialize the object'. Are both needed?
    # - defaults should be usable with anything, including sub-settings, to get an html form for a given object/setting
    # - add object/setting
    # - rename object/setting for dicts at least, but should the same mechanism be used for lists, which have order, or should there be a separate move up/move down thing?
    # - delete object/setting

