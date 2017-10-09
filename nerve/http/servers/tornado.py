#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import tornado.log
import tornado.wsgi
import tornado.ioloop
import tornado.httpserver

from nerve.http.servers.wsgi import WSGIHandler

# TODO this locks up when a request comes in...
class TornadoWSGIServer (nerve.Server):

    def __init__(self, **config):
        super().__init__(**config)

        self.username = self.get_setting("username")
        self.password = self.get_setting("password")
        self.port = self.get_setting('port')

        self.thread = nerve.Task('TornadoWSGIServerTask:' + str(self.port), target=self.run)
        self.thread.daemon = True
        self.thread.start()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('port', "Port", default=8888)
        config_info.add_setting('use_usersdb', "Use Users DB", default=True)
        config_info.add_setting('allow_guest', "Allow Guest", default=True)
        config_info.add_setting('username', "Admin Username", default='')
        config_info.add_setting('password', "Admin Password", default='')
        config_info.add_setting('ssl_enable', "SSL Enable", default=False)
        config_info.add_setting('ssl_cert', "SSL Certificate File", default='')
        config_info.add_setting('gateway', "WSGI Gateway Device Ref", default='')
        return config_info

    def run(self):
        if self.get_setting('gateway'):
            self.handler = nerve.get_object(self.get_setting('gateway'))
        else:
            self.handler = WSGIHandler(**{ 'parent': '/servers/default' })

        """
        def application(environ, start_response):
            print(environ)
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [b"<b>hello world</b>"]
        self.handler = application
        """

        tornado.log.enable_pretty_logging()
        self.container = tornado.wsgi.WSGIContainer(self.handler)
        self.server = tornado.httpserver.HTTPServer(self.container)
        self.server.listen(self.port)
        nerve.log('starting http(s) on port ' + str(self.port))

        tornado.ioloop.IOLoop.current().start()

