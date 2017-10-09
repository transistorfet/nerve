#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .controllers import DatalogController
from .devices import DatalogDevice
from .threads import DatalogThread

import nerve.modules

class Module (nerve.modules.Module):
    def __init__(self, **config):
        super().__init__(**config)
        DatalogThread().start()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        #config_info.add_setting('max_history', "Max Code History", default=20)
        #config_info.add_setting('subscriptions', "Subscriptions", default=[], itemtype='str')
        return config_info

    def update_config_data(self, config):
        super().update_config_data(config)


