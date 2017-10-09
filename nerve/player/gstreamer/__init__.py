#!/usr/bin/python3
# -*- coding: utf-8 -*-


def init():
    from .threads import GObjectThread

    thread = GObjectThread()
    thread.start()


