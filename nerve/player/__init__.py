#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .devices import PlayerDevice

def init():
    import nerve.mithril
    nerve.mithril.register_js('Player', 'nerve/player/assets/js/components.js')

