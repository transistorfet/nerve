#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .controllers.config import ConfigController
from .controllers.files import FileController
from .controllers.query import QueryController
from .controllers.pycode import PyCodeController
from .controllers.shell import ShellController

from .devices.realtime import RealtimeDevice

from .views.formview import FormView

"""
from .servers.console import Console
from .servers.tcpserver import TCPServer
from .servers.udpserver import UDPServer
"""

def init():
    pass
    #nerve.register_controller('config', ConfigController)
    #nerve.register_controller('files', FileController)

    #nerve.register_server('console', Console)
    #nerve.register_server('tcpserver', TCPServer)

