#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http

from ..models import PagesModel


class BlockView (nerve.View):
    def __init__(self, blockname, data=None):
        super().__init__()
        self._mimetype = 'text/html'
        self._blockname = blockname
        self._data = data
        self._model = PagesModel()
        self._view = None

    def render(self):
        if not self._view:
            block = self._model.get_block(self._blockname)
            self._view = nerve.http.PyHTML(None, self._data, None, code=block)
            self._view.finalize()

    def get_output(self):
        self.finalize()
        return self._view.get_output()


