#!/usr/bin/python
# -*- coding: utf-8 -*-

from controllers.config import ConfigController
from controllers.files import FileController
from controllers.query import QueryController
from controllers.pyexec import PyExecController
from controllers.shell import ShellController

from servers.console import Console
from servers.tcpserver import TCPServer
from servers.tcpclient import TCPClient
from servers.udpserver import UDPServer

def init():
    pass
    #nerve.register_controller('config', ConfigController)
    #nerve.register_controller('files', FileController)

    #nerve.register_server('console', Console)
    #nerve.register_server('tcpserver', TCPServer)

