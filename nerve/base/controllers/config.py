#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve 
import nerve.http

class ConfigController (nerve.http.Controller):
    def __init__(self, **config):
        nerve.http.Controller.__init__(self, **config)
        self.load_header("nerve/base/views/header.pyhtml", dict(tab="Config", title="Nerve Configuration"))
        self.load_footer("nerve/base/views/footer.pyhtml")

    def index(self, request):
        data = { }
        data['config_data'] = nerve.get_config_data()
        #data['config_info'] = nerve.get_config_info()
        self.load_view("nerve/base/views/config/settings.pyhtml", data)

    def save(self, request):
        # TODO do authorization check
        if request.reqtype == "POST":
            for arg in request.args.keys():
                nerve.set_config(arg, request.args[arg])
            nerve.save_config()
            self.write_json({ 'status' : 'success' })
        else:
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })

    def defaults(self, request):
        if request.reqtype != "POST":
            self.write_json({ 'status' : 'error', 'message' : "Unrecognized request type: " + request.reqtype })
            return False
        defaults = nerve.ObjectNode.get_class_config_info(request.args['type'])
        self.write_json(defaults)


