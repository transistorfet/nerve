#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import traceback

from ..msg import Colours, MsgType, Msg
from .client import IRCClient


class MooBot (IRCClient):
    def __init__(self, **config):
        super().__init__(**config)
        self.channel = '#ircmoo'

    def on_connect(self):
        self.sendmsg("JOIN " + self.channel)

    def on_name(self, nick):
        #if not nick in self.users:
        #    self.users[nick] = MooBotTerminal(self, nick)
        pass

    def on_join(self, nick):
        #if not nick in self.users:
        #    self.users[nick] = MooBotTerminal(self, nick)
        self.sendprivmsg(nick, "Welcome to the Realm!")
        self.sendprivmsg(nick, "To log in, /msg %s id <password>" % (self.nick,))
        self.sendprivmsg(nick, "Or /msg %s register <password> <email> to register a new user" % (self.nick,))

    """
    def on_part(self, nick):
        if nick in self.users:
            self.users[nick].logout()
            del(self.users[nick])

    def on_quit(self, nick):
        if nick in self.users:
            self.users[nick].logout()
            del(self.users[nick])

    def on_nick(self, old, new):
        del(self.users[old])
        self.users[new] = MooBotTerminal(self, new)
    """

    def on_privmsg(self, msg):
        try:
            if msg.args[0] == self.nick:
                self.do_guest_command(msg.text)
                #if msg.nick in self.users:
                #    self.do_guest_command(msg.text)
                #else:
                #    self.sendprivmsg(msg.nick, "I don't have a record of you.  Please try parting and rejoining " + self.channel)
            elif msg.args[0][0] == '#':
                if msg.text[0] == '!':
                    self.do_channel_command(msg)
        except:
            self.sendprivmsg(msg.nick, traceback.format_exception_only(sys.exc_type, sys.exc_value))
            nerve.log(traceback.format_exc(), logtype='error')

    def do_channel_command(self, msg):
        args = msg.text.split()
        args[0] = args[0].lower()
        if args[0] == "!channels":
            for name in self.channels.keys():
                print("DEBUG: " + self.channels[name].name)
                for user in self.channels[name].users:
                    print('\"' + user + "\"", end='')
                print(end='\n')
        # TODO you could have a !who command that tells who's playing?

    def do_guest_command(self, text):
        args = text.split()
        args[0] = args[0].lower()
        if args[0] == "login":
            if self.login(User.crypt(args[1])):
                self.notify("You are now logged in as %s" % (self.nick,))
            else:
                self.notify("Invalid password for %s" % (self.nick,))
        elif args[0] == 'register':
            if len(args) != 2:
                self.notify("Usage: register <password>")
                return
            if self.nick in User.db:
                self.notify("This nick is already registered.  Please use the login command to authenticate.")
                return
            user = User(self.nick, User.crypt(args[1]))
            user.thing = thing.user.clone()
            self.user = user.thing
            self.user.terminal = self
            self.user.name = self.nick
            task = thing.GenericTask(self, self.user, 'do_register')
            #self.attach(task)
            task.queue("")
        else:
            self.notify("You must login first.")

  
