#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve 
import nerve.http


class UsersController (nerve.http.SessionController):

    @nerve.public
    def index(self, request):
        print(self.session)
        data = { }
        #self.load_default_data(data)
        # TODO can you for this path without refering directly to the module (ie. using what's in the request)
        #self.load_html_view("nerve/base/views/config/settings.pyhtml", data)

        #data['formhtml'] = FormView(nerve.root().get_config_info()).get_output()

        self.load_template_view('nerve/base/views/users/login.blk.pyhtml', data, request)
        #self.template_add_to_section('jsfiles', '/assets/js/formview.js')

    @nerve.public
    def login(self, request):
        redirect = request.arg('redirect', '')
        if redirect and (redirect[0] != '/' or '/..' in redirect):
            redirect = ''

        if request.reqtype == "GET":
            data = { 'redirect': redirect }
            self.load_template_view('nerve/base/views/users/login.blk.pyhtml', data)
            return

        if request.reqtype != "POST":
            raise nerve.ControllerError("Unexpected request type: " + request.reqtype)

        try:
            with nerve.users.login(request.arg('username'), request.arg('password')):
                # TODO this should store a randomized token instead
                self.session['username'] = nerve.users.thread_owner()
                self.redirect_to(redirect if redirect else '/home')
        except nerve.users.UserLoginError:
            self.load_json_view({ 'notice' : "Invalid username or password" })


    @nerve.public
    def manage(self, request):
        #nerve.users.require_group('admin')

        data = { }
        data['users'] = nerve.users.get_user_list()
        data['groups'] = nerve.users.get_group_list()
        self.load_template_view('nerve/base/views/users/manage.blk.pyhtml', data)

    @nerve.public
    def dialog(self, request):
        #nerve.users.require_group('admin')

        (slug, _, idnum) = request.get_slug().partition('/')
        if idnum != '':
            try:
                idnum = int(idnum)
            except:
                raise nerve.ControllerError("invalid id in request: " + str(idnum))

            if slug not in [ 'edituser', 'editgroup', 'deleteuser', 'deletegroup' ]:
                raise nerve.ControllerError("invalid operation in request: " + str(slug))

        data = { }
        data['idnum'] = idnum
        self.load_html_view('nerve/base/views/users/{0}.blk.pyhtml'.format(slug), data)

    @nerve.public
    def edit(self, request):
        #nerve.users.require_group('admin')

        pass

