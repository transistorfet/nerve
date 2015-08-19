#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve


class PyCodeController (nerve.Controller):
    def __init__(self, **config):
        super().__init__(**config)
        self.globals = { }
        self.globals['nerve'] = nerve

    def do_request(self, request):
        self.load_plaintext_view('')
        if 'requests[]' in request.args:
            for querystr in request.args['requests[]']:
                self._view.write_text(repr(eval(querystr, self.globals)) + '\n')


