#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

from nerve.http import PyHTML


class Controller (nerve.Controller):
    def load_view(self, filename, data=None):
        self.set_mimetype('text/html')
        engine = PyHTML(filename, None, data)
        contents = engine.evaluate()
        self.write_output(contents)

