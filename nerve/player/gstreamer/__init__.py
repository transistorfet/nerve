#!/usr/bin/python3
# -*- coding: utf-8 -*-


def init():
    from .tasks import GObjectTask

    thread = GObjectTask()
    thread.start()


