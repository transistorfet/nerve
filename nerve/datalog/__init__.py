#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .controllers import DatalogController
from .devices import DatalogDevice
from .tasks import DatalogTask


#def init():
#    DatalogTask().start()

#def get_config_info(config_info):
#    return config_info

import nerve

class Module (nerve.modules.Module):
    def __init__(self, **config):
        super().__init__(**config)
        DatalogTask().start()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        #config_info.add_setting('max_history', "Max Code History", default=20)
        #config_info.add_setting('subscriptions', "Subscriptions", default=[], itemtype='str')
        return config_info

    def update_config_data(self, config):
        super().update_config_data(config)


