#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .controllers import PagesController
from .views.block import BlockView
from .views.page import PageView


#def init():
#    pass

import nerve

class Module (nerve.modules.Module):
    def __init__(self, **config):
        super().__init__(**config)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        return config_info

    def update_config_data(self, config):
        super().update_config_data(config)

