#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

from .devices import DatalogDevice


class DatalogTask (nerve.Task):
    def __init__(self):
        super().__init__("DatalogTask")

    def run(self):
        while not self.stopflag.wait(60):
            try:
                for datalog in DatalogDevice.datalogs:
                    datalog._collect_data()
            except:
                nerve.log(traceback.format_exc(), logtype='error')


