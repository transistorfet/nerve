#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve 
import nerve.http


class UsersController (nerve.http.SessionMixIn, nerve.http.Controller):

    @nerve.public
    def index(self, request):
        print(self.session)
        data = { }
        #self.load_default_data(data)
        # TODO can you for this path without refering directly to the module (ie. using what's in the request)
        #self.load_html_view("nerve/base/views/config/settings.pyhtml", data)

        #data['formhtml'] = FormView(nerve.get_main().get_config_info()).get_output()

        self.load_template_view('nerve/base/views/users/login.blk.pyhtml', data, request)
        #self.template_add_to_section('jsfiles', '/assets/js/formview.js')

    @nerve.public
    def login(self, request):
        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        try:
            with nerve.users.login(request.arg('username'), request.arg('password')):
                self.session['username'] = nerve.users.thread_owner()
                self.load_json_view({ 'status' : 'success' })
        except nerve.users.UserLoginError:
            self.load_json_view({ 'status' : "invalid username or password" })

