#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .controllers import DatalogController
from .devices import DatalogDevice
from .tasks import DatalogTask


def init():
    DatalogTask().start()

def get_config_info(config_info):
    return config_info


#init()

