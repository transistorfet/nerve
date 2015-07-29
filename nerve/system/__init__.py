#!/usr/bin/python3
# -*- coding: utf-8 -*-

import platform

if platform.system() == "Windows":
    from ._windows.devices import SystemDevice
else:
    from ._linux.devices import SystemDevice


