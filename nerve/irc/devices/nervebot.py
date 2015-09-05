#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import traceback

from ..msg import Colours, MsgType, Msg
from .client import IRCClient


class NerveBot (IRCClient):
    def __init__(self, **config):
        super().__init__(**config)
        self.channel = '#ircmoo'
        self.linebuffer = [ ]
        if not self.get_child('event_privmsg'):
            self.set_child('event_privmsg', nerve.Module.make_object('objects/ObjectNode', dict()))

    def on_connect(self):
        self.sendmsg("JOIN " + self.channel)

    def on_name(self, nick):
        pass

    def on_join(self, nick):
        pass

    def on_part(self, nick):
        pass

    def on_quit(self, nick):
        pass

    def on_nick(self, nick):
        pass

    def on_privmsg(self, msg):
        self.linebuffer.append(msg.text.rstrip())
        if len(self.linebuffer) > 100:
            self.linebuffer = self.linebuffer[len(self.linebuffer) - 100:]
        self.notify('event_privmsg/*', msg)

    def on_notice(self, msg):
        pass


