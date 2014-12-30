#!/usr/bin/python
# -*- coding: utf-8 -*-

import platform

if platform.system() == "Windows":
    from windows.system import SystemDevice
else:
    from linux.system import SystemDevice


