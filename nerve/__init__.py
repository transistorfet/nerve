#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import 

import sys
import time
stdout = sys.stdout

def log(text):
    global stdout
    stdout.write(time.strftime("%Y-%m-%d %H:%M") + " " + text + "\n")

from nerve.objects import ConfigInfo, ObjectNode, SymbolicLink, Module, ModulesDirectory
from nerve.core import Request, Controller, Server, Model, Device, QueryObject, NotFoundException
from nerve.tasks import Task
from nerve.events import Event
from nerve.db import Database
from nerve.users import Users
from nerve.main import Main, loop, quit, main, get_config_info, get_config_data, save_config, configdir, set_object, get_object, del_object, has_object, query, query_string, read_config_file, write_config_file

