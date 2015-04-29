#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve 
import nerve.http

class ConfigController (nerve.http.Controller):
    def __init__(self, **config):
        nerve.http.Controller.__init__(self, **config)
        #self.load_header("nerve/base/views/header.pyhtml", dict(tab="Config", title="Nerve Configuration"))
        #self.load_footer("nerve/base/views/footer.pyhtml")

        #self.add_css("nerve/http/assets/css/widgets.css", 'global')    # you'd need like a default set of files that all subfiles will have
        #self.add_js("nerve/base/assets/js/config.js")

    def index(self, request):
        data = { }
        #self.load_default_data(data)
        # TODO can you for this path without refering directly to the module (ie. using what's in the request)
        self.load_view("nerve/base/views/config/settings.pyhtml", data)

    def types(self, request):
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
        else:
            typelist = nerve.Modules.get_types(nerve.Device)
            self.write_json(typelist)

    def defaults(self, request):
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
        elif not request.arg('type'):
            self.write_json({ 'status' : 'error', 'message' : "You must select a type first" })
        else:
            defaults = nerve.ObjectNode.get_class_config_info(request.arg('type'))
            self.write_json(defaults.settings)

    def create(self, request):
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
            return False

        dirname = request.arg('__dir__')
        name = request.arg('__name__')
        typeinfo = request.arg('__type__')

        if not dirname or not nerve.has_object(dirname):
            self.write_json({ 'status' : 'error', 'message' : "The directory you've specified is invalid." })
            return False
        if not name:
            self.write_json({ 'status' : 'error', 'message' : "You must provide a valid name." })
            return False
        if nerve.has_object(dirname + '/' + name):
            self.write_json({ 'status' : 'error', 'message' : "An object of that name already exists." })
            return False
        if not typeinfo:
            self.write_json({ 'status' : 'error', 'message' : "You must select a type." })
            return False

        defaults = nerve.ObjectNode.get_class_config_info(typeinfo)
        config = { '__type__' : typeinfo }
        self._unpack_values(defaults, config, request.args)

        obj = nerve.ObjectNode.make_object(typeinfo, config)
        nerve.set_object(dirname + '/' + name, obj)
        nerve.save_config()
        self.write_json({ 'status' : 'success' })

    def rename(self, request):
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
            return False

        # TODO you totally don't validate these names enough
        oldname = request.arg('oldname')
        newname = request.arg('newname')

        if not oldname or not nerve.has_object(oldname):
            self.write_json({ 'status' : 'error', 'message' : "The directory you've specified is invalid." })
            return False
        if not newname:
            self.write_json({ 'status' : 'error', 'message' : "The new name given is invalid." })
            return False
        if nerve.has_object(newname):
            self.write_json({ 'status' : 'error', 'message' : "An object of that name already exists." })
            return False

        obj = nerve.get_object(oldname)
        if not nerve.del_object(oldname):
            self.write_json({ 'status' : 'error', 'message' : "Unable to rename this object." })
            return False
        nerve.set_object(newname, obj)
        nerve.save_config()
        self.write_json({ 'status' : 'success' })

    def save(self, request):
        # TODO do authorization check
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
            return False

        obj = nerve.get_object(request.args['objectname'])
        defaults = obj.get_config_info()
        config = obj.get_config_data()
        self._unpack_values(defaults, config, request.args)

        obj.set_config_data(config)
        nerve.save_config()
        self.write_json({ 'status' : 'success' })

    def delete(self, request):
        # TODO do authorization check
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
            return False

        objectname = request.args['objectname']
        if not objectname or not nerve.has_object(objectname):
            self.write_json({ 'status' : 'error', 'message' : "The object you've specified doesn't exist." })
            return False

        result = nerve.del_object(objectname)
        if result:
            nerve.save_config()
            self.write_json({ 'status' : 'success' })
        else:
            self.write_json({ 'status' : 'error', 'message' : "Unable to delete object." })

    def _unpack_values(self, defaults, config, args):
        for setting in defaults.settings:
            if setting['name'] in args:
                # TODO also check sanity and convert to int if necessary
                if setting['datatype'] == 'int':
                    config[setting['name']] = int(args[setting['name']])
                elif setting['datatype'] == 'float':
                    config[setting['name']] = float(args[setting['name']])
                else:
                    config[setting['name']] = args[setting['name']]
        return config

