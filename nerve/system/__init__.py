#!/usr/bin/python3
# -*- coding: utf-8 -*-

import platform

if platform.system() == "Windows":
    from .windows import devices
else:
    from .linux import devices

