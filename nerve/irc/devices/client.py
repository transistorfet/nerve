#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import time
import socket
import select
import traceback

import cgi
import json
import mimetypes

import urllib.parse

from ..msg import Colours, MsgType, Msg


class Channel (object):
    def __init__(self, name):
        self.name = name
        self.mode = ""
        self.users = [ ]

    def join(self, name):
        if not name in self.users:
            self.users.append(name)

    def part(self, name):
        if name in self.users:
            self.users.remove(name)


class IRCClient (nerve.Device):
    version = "0.1"
    start_time = time.time()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('nick', "Client Nick", default='TheRealm')
        config_info.add_setting('server', "Server URI", default='irc.foonetic.net:6667')

        """
        server_list = nerve.objects.StructConfigType()
        server_list.add_setting('hostname', "Hostname", default='')
        server_list.add_setting('port', "Port", default=6667)
        server_list.add_setting('password', "Password (optional)", default='')
        """
        return config_info

    def __init__(self, **config):
        super().__init__(**config)
        self.nick = self.get_setting('nick')

        self.connected = False
        self.mode = ""
        self.socket = None
        self.servers = [ self.get_setting('server') ]
        self.channels = { }
        self.lastcontact = time.time()

        self.thread = IRCClientTask(self)
        self.thread.start()

    def connect(self, hostname, port):
        if self.socket:
            self.close()

        self.connected = False
        self.hostname = hostname
        self.port = int(port)
        self.socket = socket.create_connection((hostname, int(port)))
        self.rfile = self.socket.makefile(mode='r', encoding='utf-8', newline='\r\n')

        self.sendmsg("NICK %s" % (self.nick,))
        self.sendmsg("USER %s 0 0 :IRCMoo v%s (transistor)" % (self.nick, self.version))
        #self.sendmsg("MODE %s +b" % (self.nick,))

    def close(self):
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.socket.close()
            self.connected = False

    def readmsg(self):
        line = self.rfile.readline()
        if line == None:
            return None
        line = line.strip('\r\n')
        nerve.log(" IN: " + line)
        return Msg(line)

    def sendmsg(self, data):
        if type(data) == Msg:
            # TODO self.socket.send(data.marshal())
            raise NotImplementedError
        nerve.log("OUT: " + repr(data.rstrip()))
        self.socket.send(bytes(data + "\r\n", 'utf-8'))

    def sendprivmsg(self, target, text):
        self.sendmsg("PRIVMSG %s :%s" % (target, text))

    def sendnotice(self, target, text):
        self.sendmsg("NOTICE %s :%s" % (target, text))

    def dispatch(self, msg):
        if msg.cmd == "PING":
            return self.sendmsg(msg.line.replace("PING", "PONG"))
        elif msg.cmd == "PRIVMSG":
            if msg.nargs < 1:
                return
            self.on_privmsg(msg)
        elif msg.cmd == "NOTICE":
            if msg.nargs < 1:
                return
            self.on_notice(msg)
        elif msg.cmd == "JOIN":
            if msg.nargs < 1:
                return
            channel = msg.args[0]
            if msg.nick == self.nick:
                if channel not in self.channels:
                    self.channels[channel] = Channel(channel)
            else:
                self.channels[channel].join(msg.nick)
                self.on_join(msg.nick)
        elif msg.cmd == "PART":
            if msg.nargs < 1:
                return
            channel = msg.args[0]
            if msg.nick == self.nick:
                # TODO rejoin??
                pass
            else:
                self.channels[channel].part(msg.nick)
                self.on_part(msg.nick)
        elif msg.cmd == "QUIT":
            for channel in self.channels:
                channel.part(msg.nick)
            self.on_quit(msg.nick)
        elif msg.cmd == "MODE":
            self.mode = msg.text
        elif msg.cmd == "NICK":
            self.on_nick(msg.nick, msg.args[0])
        elif msg.cmd == str(MsgType.RPL_NAMREPLY):
            if msg.nargs != 4:
                return
            channel = msg.args[2]
            for nick in msg.args[3].split():
                self.channels[channel].join(nick)
                self.on_name(nick)
        elif msg.cmd == str(MsgType.ERR_NICKNAMEINUSE):
            nerve.log("IRC: nick %s in use on server %s." % (self.nick, self.hostname))
            # TODO add better altnick handling
            self.nick = self.nick + "_"
            self.sendmsg("NICK " + self.nick)
        elif msg.cmd == str(MsgType.RPL_ENDOFMOTD):
            self.connected = True
            nerve.log("IRC: Connection complete to server " + self.hostname)
            self.on_connect()

    def on_connect(self):
        pass

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
        pass

    def on_notice(self, msg):
        pass


class IRCClientTask (nerve.Task):
    def __init__(self, client):
        super().__init__('IRCClientTask')
        self.client = client

    def connect_any(self):
        while not self.stopflag.is_set():
            for address in self.client.servers:
                (hostname, port) = address.split(':', 1)
                #url = urllib.parse.urlparse(address)
                try:
                    nerve.log("connecting to " + hostname + ":" + port)
                    self.client.connect(hostname, port)
                    return

                except OSError as e:
                    nerve.log("error connecting to " + hostname + ":" + port + ": " + str(e))
            self.stopflag.wait(10)

    def run(self):
        while not self.stopflag.is_set():
            self.connect_any()

            while not self.stopflag.is_set():
                try:
                    msg = self.client.readmsg()
                    if not msg:
                        break
                    self.client.lastcontact = time.time()
                    self.client.dispatch(msg)
                except:
                    nerve.log("error on irc server connection to " + self.client.hostname + ":" + str(self.client.port))
                    nerve.log(traceback.format_exc())
                    self.client.close()
                    break
            self.stopflag.wait(10)

    def stop(self):
        self.client.close()
        super().stop()


