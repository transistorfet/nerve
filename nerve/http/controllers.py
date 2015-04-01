#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

from nerve.http import PyHTML


class Controller (nerve.Controller):
    def __init__(self, **config):
        nerve.Controller.__init__(self, **config)
        self.header_bytes = None
        self.footer_bytes = None

    """
    @staticmethod
    def get_config_info():
        config_info = nerve.Controller.get_config_info()
        config_info.add_setting('header', "Header File")
        config_info.add_setting('footer', "Footer File")
        return config_info
    """

    def load_view(self, filename, data=None):
        self.set_mimetype('text/html')
        engine = PyHTML(filename, None, data)
        contents = engine.evaluate()
        self.write_text(contents)

    def load_header(self, filename, data=None):
        engine = PyHTML(filename, None, data)
        self.header_bytes = bytes(engine.evaluate(), 'utf-8')

    def load_footer(self, filename, data=None):
        engine = PyHTML(filename, None, data)
        self.footer_bytes = bytes(engine.evaluate(), 'utf-8')

    def get_output(self):
        output = nerve.Controller.get_output(self)
        if self.mimetype == 'text/html':

            """
            header = self.get_setting('header')
            if header and not self.header_bytes:
                engine = PyHTML(header, None, None)
                self.header_bytes = bytes(engine.evaluate(), 'utf-8')

            footer = self.get_setting('footer')
            if footer and not self.footer_bytes:
                engine = PyHTML(footer, None, None)
                self.footer_bytes = bytes(engine.evaluate(), 'utf-8')
            """

            if self.header_bytes:
                output = self.header_bytes + output
            if self.footer_bytes:
                output = output + self.footer_bytes

        return output


