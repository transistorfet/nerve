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

        """
        if not self.get_child('event_privmsg'):
            self.set_child('event_privmsg', nerve.ObjectNode.make_object('objects/ObjectNode', dict()))
        """

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_default_child('event_privmsg', { '__type__': 'objects/ObjectNode' })
        config_info.add_default_child('event_notice', { '__type__': 'objects/ObjectNode' })

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
        self._buffer_line(msg.text.rstrip())
        self.query('event_privmsg/*', msg)

    def on_notice(self, msg):
        self._buffer_line(msg.text.rstrip())
        self.query('event_notice/*', msg)

    def _buffer_line(self, line):
        self.linebuffer.append(line)
        if len(self.linebuffer) > 100:
            self.linebuffer = self.linebuffer[len(self.linebuffer) - 100:]

