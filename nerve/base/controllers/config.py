#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve 
import nerve.http

class ConfigController (nerve.http.Controller):
    def __init__(self, **config):
        nerve.http.Controller.__init__(self, **config)
        #self.load_header("nerve/base/views/header.pyhtml", dict(tab="Config", title="Nerve Configuration"))
        #self.load_footer("nerve/base/views/footer.pyhtml")

    def index(self, request):
        data = { }
        data['config_data'] = nerve.get_config_data()
        #data['config_info'] = nerve.get_config_info()
        self.load_view("nerve/base/views/config/settings.pyhtml", data)

    def save(self, request):
        # TODO do authorization check
        if request.reqtype == "POST":
            obj = nerve.get_object(request.args['objectname'])
            defaults = obj.get_config_info()
            config = obj.get_config_data()
            for arg in defaults.settings:
                if arg['name'] in request.args:
                    # TODO also check sanity and convert to int if necessary
                    config[arg['name']] = request.args[arg['name']]
            obj.set_config_data(config)
            nerve.save_config()
            self.write_json({ 'status' : 'success' })
        else:
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })

    def create(self, request):
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
            return False

        dirname = request.arg('__dir__')
        name = request.arg('__name__')
        typeinfo = request.arg('__type__')

        if not name:
            self.write_json({ 'status' : 'error', 'message' : "You must provide a valid name." })
            return False
            

        defaults = nerve.ObjectNode.get_class_config_info(typeinfo)
        config = { '__type__' : typeinfo }
        for arg in defaults.settings:
            if arg['name'] in request.args:
                # TODO also check sanity and convert to int if necessary
                config[arg['name']] = request.args[arg['name']]

        obj = nerve.ObjectNode.make_object(typeinfo, config)
        nerve.set_object(dirname + '/' + name, obj)
        nerve.save_config()
        self.write_json({ 'status' : 'success' })

    def defaults(self, request):
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
            return False
        defaults = nerve.ObjectNode.get_class_config_info(request.args['type'])
        self.write_json(defaults.settings)

    def types(self, request):
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
            return False
        #defaults = nerve.ObjectNode.get_class_config_info(request.args['type'])
        typelist = nerve.Modules.get_types(nerve.Device)
        self.write_json(typelist)


