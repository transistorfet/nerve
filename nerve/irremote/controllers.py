#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

import sys
import os.path
import traceback

import urllib
import urllib.parse


class IRRemoteController (nerve.http.Controller):

    @nerve.public
    def index(self, request):
        irremote = nerve.get_object('/devices/irremote')

        data = { }
        data['remotelist'] = irremote.get_remote_names()
        data['codelist'] = irremote.get_recent_codes()
        data['program_mode'] = irremote.program_mode

        self.load_template_view('nerve/irremote/views/codes.blk.pyhtml', data, request)
        self.template_add_to_section('jsfiles', '/irremote/assets/js/irremote.js')
        self.template_add_to_section('jsfiles', '/assets/js/formview.js')
        self.template_add_to_section('cssfiles', '/irremote/assets/css/irremote.css')

    @nerve.public
    def get_recent_codes(self, request):
        irremote = nerve.get_object('/devices/irremote')

        try:
            last_update = float(request.args['last_update'])
        except:
            raise nerve.ControllerError("You must provide the 'last_update' argument as a float.") from None

        data = { }
        data['remotelist'] = irremote.get_remote_names()
        data['codelist'] = irremote.get_recent_codes(last_update, wait=60)

        self.load_html_view('nerve/irremote/views/coderows.blk.pyhtml', data)

    @nerve.public
    def clear_recent_codes(self, request):
        irremote = nerve.get_object('/devices/irremote')
        irremote.clear_recent_codes()
        self.load_json_view({ 'notice' : "Recent codes cleared." })

    @nerve.public
    def get_saved_codes(self, request):
        irremote = nerve.get_object('/devices/irremote')

        data = { }
        data['remotelist'] = irremote.get_remote_names()
        data['codelist'] = irremote.get_saved_codes(request.arg('remote_name'))

        self.load_html_view('nerve/irremote/views/coderows.blk.pyhtml', data)

    @nerve.public
    def save_names(self, request):
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        codelist = request.arg('codelist')
        if not codelist:
            raise nerve.ControllerError("You must provide the 'codelist' argument.")

        errors = [ ]
        irremote = nerve.get_object('/devices/irremote')
        for (code, remote_name, button_name) in codelist:
            if code:
                result = irremote.set_button_name(code, remote_name, button_name)
                if result:
                    errors.append("Button name " + remote_name + ":" + button_name + " is already assigned to code " + result)
        if len(errors) > 0:
            self.load_json_view({ 'error' : '<br/>\n'.join(errors) })
        else:
            self.load_json_view({ 'notice' : 'Changes have been saved' })

    @nerve.public
    def delete_code(self, request):
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        code = request.arg('code')
        if not code:
            raise nerve.ControllerError("You must provide the 'code' argument.")

        irremote = nerve.get_object('/devices/irremote')
        irremote.delete_code(code)
        self.load_json_view({ 'notice' : code + ' has been deleted' })

    @nerve.public
    def add_remote(self, request):
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        remote_name = request.arg('remote_name')
        if not remote_name:
            raise nerve.ControllerError("You must provide the 'remote_name' argument.")

        irremote = nerve.get_object('/devices/irremote')
        if irremote.add_remote(remote_name):
            self.load_json_view({ 'notice' : "Remote " + remote_name + " has been added.", 'remote_name': remote_name })
        else:
            self.load_json_view({ 'error' : "A remote by that name already exists." })

    @nerve.public
    def remove_remote(self, request):
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        remote_name = request.arg('remote_name')
        if not remote_name:
            raise nerve.ControllerError("You must provide the 'remote_name' argument.")

        irremote = nerve.get_object('/devices/irremote')
        irremote.remove_remote(remote_name)
        self.load_json_view({ 'notice' : "Remote " + remote_name + " has been removed.", 'remote_name': remote_name })

    @nerve.public
    def edit_action(self, request):
        code = request.get_slug()
        if not code:
            raise nerve.ControllerError("You must provide a IR code")

        path = '/devices/irremote/' + code
        try:
            obj = nerve.get_object(path)
        except AttributeError:
            obj = nerve.ObjectNode.make_object("asyncs/PyCodeAsyncTask", { })

        #self.set_view(nerve.base.FormView(obj.get_config_info(), obj.get_config_data(), '/config/save' + path, submitback=True))
        #self.load_template_view(None, None, request)
        #self.template_add_to_section('jsfiles', '/assets/js/formview.js')
        #self.template_add_to_section('content', nerve.base.FormView(obj.get_config_info(), obj.get_config_data(), '/irremote/save_action/' + code, submitback=True))
        self.set_view(nerve.base.FormView(obj.get_config_info(), obj.get_config_data(), '/irremote/save_action/' + code, textbefore="<h5>Event for {0}</h5>".format(code)))
        #self.set_view(nerve.base.FormView(obj.get_config_info(), obj.get_config_data(), '/irremote/save_action/' + code, textbefore='<div><script type="text/javascript" src="/assets/js/formview.js"></script>', textafter='</div>'))

    @nerve.public
    def save_action(self, request):
        nerve.users.require_group('admin')

        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        code = request.get_slug()
        if not code:
            raise nerve.ControllerError("You must provide a valid object name")

        """
        path = '/events/ir/irrecv/' + code
        try:
            obj = nerve.get_object(path)
            config = obj.get_config_info().validate(request.args)
            obj.update_config_data(config)
        except AttributeError:
            defaults = nerve.ObjectNode.get_class_config_info('asyncs/PyCodeAsyncTask')
            config = defaults.validate(request.args)
            obj = nerve.ObjectNode.make_object('asyncs/PyCodeAsyncTask', config)
            nerve.set_object(path, obj)

        nerve.save_config()
        self.load_json_view({ 'notice': "Event added" })
        """

        irremote = nerve.get_object('/devices/irremote')
        defaults = nerve.ObjectNode.get_class_config_info('asyncs/PyCodeAsyncTask')
        config = defaults.validate(request.args)
        config['__type__'] = 'asyncs/PyCodeAsyncTask'
        irremote.set_action(code, config)
        self.load_json_view({ 'notice': "Action added" })

    @nerve.public
    def toggle_program_mode(self, request):
        irremote = nerve.get_object('/devices/irremote')
        if irremote.program_mode:
            irremote.program_mode = False
        else:
            irremote.program_mode = True
        self.load_json_view({ 'program_mode': irremote.program_mode })

    @nerve.public
    def send_code(self, request):
        code = request.arg('code')
        if not code:
            raise nerve.ControllerError("You must provide an IR code")

        #irremote = nerve.get_object('/devices/irremote')
        nerve.query('/devices/rgb/ir', code)
        self.load_json_view({ 'notice' : "Code sent." })


