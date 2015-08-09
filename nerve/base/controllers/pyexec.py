#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve


class PyExecController (nerve.Controller):
    def __init__(self, **config):
        super().__init__(**config)
        self.globals = { }
        self.globals['nerve'] = nerve

    def do_request(self, request):
        result = None
        self.set_mimetype('text/plain')
        if 'queries[]' in request.args:
            result = [ ]
            for querystr in request.args['queries[]']:
                self.write_text(repr(eval(querystr, self.globals)) + '\n')


