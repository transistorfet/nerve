
from __future__ import absolute_import 

from nerve.core import *
from nerve.server import *
from nerve.console import *
from nerve.devices.layout import *
from nerve.devices.serialdev import *

Namespace.root = Namespace();

def add_device(name, device):
    Namespace.root.add(name, device)

def get_device(name):
    return Namespace.root.get(name)

def query(line, addr=None, server=None):
    Namespace.root.query(line, addr, server)

def dispatch(msg):
    Namespace.root.dispatch(msg)

def loop():
    Console.loop()

