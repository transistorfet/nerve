#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

from .devices import DatalogDevice


class DatalogThread (nerve.Thread):
    def __init__(self):
        super().__init__("DatalogThread")

    def run(self):
        while not self.stopflag.wait(60):
            try:
                for datalog in DatalogDevice.datalogs:
                    datalog._collect_data()
            except:
                nerve.log(traceback.format_exc(), logtype='error')


