#!/usr/bin/python
# -*- coding: utf-8 -*-

import platform

if platform.system() == "Windows":
    from .windows.devices import SystemDevice
else:
    from .linux.devices import SystemDevice


