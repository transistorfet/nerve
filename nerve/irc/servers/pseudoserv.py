

# TODO this is the pseudoserv from ircmoo.  It's a base from which to make a server module

import os
import sys
import sha
import time
import socket
import thread
import traceback

from core import *

class IRCMsg:
    RPL_WELCOME =		001
    RPL_YOURHOST =		002
    RPL_CREATED =		003
    RPL_MYINFO =		004
    RPL_BOUNCE =		005
    
    RPL_TRACELINK =		200
    RPL_TRACECONNECTING =	201
    RPL_TRACEHANDSHAKE =	202
    RPL_TRACEUNKNOWN =		203
    RPL_TRACEOPERATOR =		204
    RPL_TRACEUSER =		205
    RPL_TRACESERVER =		206
    RPL_TRACESERVICE =		207
    RPL_TRACENEWTYPE =		208
    RPL_TRACECLASS =		209
    RPL_TRACERECONNECT =	210
    RPL_STATSLINKINFO =		211
    RPL_STATSCOMMANDS =		212
    RPL_ENDOFSTATS =		219
    RPL_UMODEIS =		221
    RPL_SERVLIST =		234
    RPL_SERVLISTEND =		235
    RPL_STATSUPTIME =		242
    RPL_STATSOLINE =		243
    RPL_LUSERCLIENT =		251
    RPL_LUSEROP =		252
    RPL_LUSERUNKNOWN =		253
    RPL_LUSERCHANNELS =		254
    RPL_LUSERME =		255
    RPL_ADMINME =		256
    RPL_ADMINLOC1 =		257
    RPL_ADMINLOC2 =		258
    RPL_ADMINEMAIL =		259
    RPL_TRYAGAIN =		263
    RPL_TRACELOG =		261
    RPL_TRACEEND =		262
    
    RPL_AWAY =			301
    RPL_USERHOST =		302
    RPL_ISON =			303
    RPL_UNAWAY =		305
    RPL_NOAWAY =		306
    RPL_WHOISUSER =		311
    RPL_WHOISSERVER =		312
    RPL_WHOISOPERATOR =		313
    RPL_WHOWASUSER =		314
    RPL_ENDOFWHO =		315
    RPL_WHOISIDLE =		317
    RPL_ENDOFWHOIS =		318
    RPL_WHOISCHANNELS =		319
    RPL_WHOISSPECIAL =		320
    RPL_LISTSTART =		321
    RPL_LIST =			322
    RPL_ENDOFLIST =		323
    RPL_CHANNELMODEIS =		324
    RPL_UNIQOPIS =		325
    RPL_NOTOPIC =		331
    RPL_TOPIC =			332
    RPL_INVITING =		341
    RPL_SUMMONING =		342
    RPL_INVITELIST =		346
    RPL_ENDOFINVITELIST =	347
    RPL_EXCEPTLIST =		348
    RPL_ENDOFEXCEPTLIST =	349
    RPL_VERSION =		351
    RPL_WHOREPLY =		352
    RPL_NAMREPLY =		353
    RPL_LINKS =			364
    RPL_ENDOFLINKS =		365
    RPL_ENDOFNAMES =		366
    RPL_BANLIST =		367
    RPL_ENDOFBANLIST =		368
    RPL_ENDOFWHOWAS =		369
    RPL_INFO =			371
    RPL_MOTD =			372
    RPL_ENDOFINFO =		374
    RPL_MOTDSTART =		375
    RPL_ENDOFMOTD =		376
    RPL_YOUREOPER =		381
    RPL_REHASHING =		382
    RPL_YOURESERVICE =		383
    RPL_TIME =			391
    RPL_USERSSTART =		392
    RPL_USERS =			393
    RPL_ENDOFUSERS =		394
    RPL_NOUSERS =		395
    
    ERR_NOSUCHNICK =		401
    ERR_NOSUCHSERVER =		402
    ERR_NOSUCHCHANNEL =		403
    ERR_CANNOTSENDTOCHAN =	404
    ERR_TOOMANYCHANNELS =	405
    ERR_WASNOSUCHNICK =		406
    ERR_TOOMANYTARGETS =	407
    ERR_NOSUCHSERVICE =		408
    ERR_NOORIGIN =		409
    ERR_NORECIPIENT =		411
    ERR_NOTEXTTOSEND =		412
    ERR_NOTOPLEVEL =		413
    ERR_WILDTOPLEVEL =		414
    ERR_BADMASK =		415
    ERR_UNKNOWNCOMMAND =	421
    ERR_NOMOTD =		422
    ERR_NOADMININFO =		423
    ERR_FILEERROR =		424
    ERR_NONICKNAMEGIVEN =	431
    ERR_ERRONEUSNICKNAME =	432
    ERR_NICKNAMEINUSE =		433
    ERR_NICKCOLLISION =		436
    ERR_UNAVAILRESOURCE	 =	437
    ERR_USERNOTINCHANNEL =	441
    ERR_NOTONCHANNEL =		442
    ERR_USERONCHANNEL =		443
    ERR_NOLOGIN =		444
    ERR_SUMMONDISABLED =	445
    ERR_USERDISABLED =		446
    ERR_NOTREGISTERED =		451
    ERR_NEEDMOREPARAMS =	461
    ERR_ALREADYREGISTERED =	462
    ERR_NOPERMFORHOST =		463
    ERR_PASSWDMISMATCH =	464
    ERR_YOUREBANNEDCREEP =	465
    ERR_YOUWILLBEBANNED =	466
    ERR_KEYSET =		467
    ERR_CHANNELISFULL =		471
    ERR_UNKNOWNMODE =		472
    ERR_INVITEONLYCHAN =	473
    ERR_BANNEDFROMCHAN =	474
    ERR_BADCHANNELKEY =		475
    ERR_BADCHANMASK =		476
    ERR_NOCHANMODES =		477
    ERR_BANLISTFULL =		478
    ERR_NOPRIVILEGES =		481
    ERR_CHANOPRIVSNEEDED =	482
    ERR_CANTKILLSERVER =	483
    ERR_RESTRICTED =		484
    ERR_UNIQOPPRIVSNEEDED =	485
    ERR_NOOPERHOST =		491
    ERR_UMODEUNKNOWNFLAG =	501
    ERR_USERSDONTMATCH =	502

    cmdlist = { \
	"PASS" : (0, 1, 1), \
	"NICK" : (0, 0, 1), \
	"USER" : (1, 4, 4), \
	"OPER" : (0, 2, 2), \
	"QUIT" : (1, 0, 1), \
	"SQUIT" : (1, 2, 2), \
	"JOIN" : (0, 1, 2), \
	"PART" : (1, 1, 2), \
	"MODE" : (0, 1, 0), \
	"TOPIC" : (1, 1, 2), \
	"NAMES" : (0, 0, 2), \
	"LIST" : (0, 0, 2), \
	"INVITE" : (0, 2, 2), \
	"KICK" : (1, 2, 3), \
	"PRIVMSG" : (1, 0, 2), \
	"NOTICE" : (1, 0, 2), \
	"MOTD" : (0, 0, 1), \
	"LUSERS" : (0, 0, 2), \
	"VERSION" : (0, 0, 1), \
	"STATS" : (0, 0, 2), \
	"LINKS" : (0, 0, 2), \
	"TIME" : (0, 0, 1), \
	"CONNECT" : (0, 2, 3), \
	"TRACE" : (0, 0, 1), \
	"ADMIN" : (0, 0, 1), \
	"INFO" : (0, 0, 1), \
	"SERVLIST" : (0, 0, 2), \
	"SQUERY" : (1, 0, 2), \
	"WHO" : (0, 0, 2), \
	"WHOIS" : (0, 0, 2), \
	"WHOWAS" : (0, 0, 3), \
	"KILL" : (1, 2, 2), \
	"PING" : (1, 0, 2), \
	"PONG" : (1, 0, 2), \
	"ERROR" : (1, 1, 1), \
    }

    def __init__(self, line=None):
	self.clear()
	if line:
	    self.unmarshal(line)

    def clear(self):
	self.nick = None
	self.host = None
	self.cmd = ''
	self.args = [ ]
	self.nargs = 0
	self.text = ''

    def unmarshal(self, line):
	remain = line
	if remain[0] == ':':
	    (id, remain) = remain.split(None, 1)
	    (self.nick, self.host) = id[1:].split('!')
	parts = remain.split(None, 1)
	self.cmd = parts[0]
	if len(parts) > 1:
	    parts = parts[1].split(':', 1)
	    self.args = parts[0].split()
	    if len(parts) > 1:
		self.args.append(parts[1])
		cmdinfo = self.cmdlist.get(self.cmd)
		if cmdinfo and cmdinfo[0]:
		    self.text = self.args[-1]
	self.nargs = len(self.args)
	#print line
	#print self.args
	#print "%s %s  %s %s" % (self.nick, self.host, self.cmd, self.text)

    def needs_more_params(self):
	cmd = self.cmdlist.get(self.cmd)
	if cmd and self.nargs < cmd[1]:
	    return 1
	return 0


class PseudoServ (Connection):
    host = "moo.jabberwocky.ca"
    version = "0.1"
    start_time = time.time()

    def _reset(self):
	self.user = None
	self.password = ''
	self.nick = ''
	self.realname = ''

    def __init__(self, socket, addr):
	Connection.__init__(self, socket, addr)
	self._reset()

    def close(self, reason=None):
	if self.user:
	    self.user.do_disconnect()
	if reason:
	    self.send("ERROR :Closing Link: %s\r\n" % (reason,))
	else:
	    self.send("ERROR :Closing Link: %s[%s] (Quit: )\r\n" % (self.nick, self.host))
	Connection.close(self)
	self._reset()

    def send(self, data):
	print "OUT: " + data.rstrip()
	Connection.send(self, data)

    def readmsg(self):
	line = self.readline()
	print "IN: " + line
	return IRCMsg(line)

    # STATUS:	NOTIFY THAT STATUS MESSAGE <text> FROM <channel/None=server>
    # SAY:	NOTIFY THAT <subject> HAS SAID <text> IN <channel/query>
    # EMOTE:	NOTIFY THAT <subject> HAS DONE <text> IN <channel/query>
    # JOIN:	NOTIFY THAT <subject> HAS JOINED <channel>
    # LEAVE:	NOTIFY THAT <subject> HAS LEFT <channel>
    # QUIT:	NOTIFY THAT <subject> HAS QUIT WITH MESSAGE <text>
    def notify(self, type, subject_name, channel_name, text):
	if type == 'STATUS':
	    if not channel_name:
		self.send(":TheRealm!realm@%s NOTICE %s :*** %s\r\n" % (self.host, self.nick, text))
	    else:
		self.send(":TheRealm!realm@%s PRIVMSG %s :*** %s\r\n" % (self.host, channel_name, text))
	elif type == 'SAY':
	    ### We don't send a message if it was said by our user, since the IRC client will echo that message itself
	    if not subject_name or subject_name == self.nick or not channel_name:
		return
	    self.send(":%s!~%s@%s PRIVMSG %s :%s\r\n" % (subject_name, subject_name, self.host, channel_name, text))
	elif type == 'EMOTE':
	    ### We don't send a message if it was said by our user, since the IRC client will echo that message itself
	    if not subject_name or subject_name == self.nick or not channel_name:
		return
	    self.send(":%s!~%s@%s PRIVMSG %s :\x01\x41\x43TION %s\x01\r\n" % (subject_name, subject_name, self.host, channel_name, text))
	elif type == 'JOIN':
	    ### Notify the connection that the user has joined a channel
	    self.send(":%s!~%s@%s JOIN :%s\r\n" % (self.nick, self.nick, self.host, channel_name))
	    # TODO send topic
	    self._send_names(channel_name)
	elif type == 'LEAVE':
	    ### Notify the connection that the user has left a channel
	    self.send(":%s!~%s@%s PART %s\r\n" % (self.nick, self.nick, self.host, channel_name))

    def _dispatch(self, msg):
	if msg.needs_more_params():
	    return self.send(":%s %03d %s :Not enough parameters\r\n" % (self.host, IRCMsg.ERR_NEEDMOREPARAMS, msg.args[0]))
	if msg.cmd == "PING":
	    if msg.nargs != 1:
		return self.send(":%s %03d %s :No such server\r\n" % (self.host, IRCMsg.ERR_NOSUCHSERVER, msg.args[0]))
	    return self.send(":%s PONG %s :%s\r\n" % (self.host, self.host, msg.args[0]))
	if self.user:
	    self._dispatch_user(msg)
	else:
	    self._dispatch_guest(msg)

    def _dispatch_guest(self, msg):
	if msg.cmd == "PASS":
	    self.password = User.crypt(msg.args[0])
	elif msg.cmd == "NICK":
	    if not User.validname(msg.args[0]):
		return self.send(":%s %03d %s :Erroneus nickname\r\n" % (self.host, IRCMsg.ERR_ERRONEUSNICKNAME, msg.args[0]))
	    self.nick = msg.args[0]
	    if self.realname:
		self._login()
	elif msg.cmd == "USER":
	    self.realname = msg.args[3]
	    if self.nick:
		self._login()
	elif msg.cmd == "PRIVMSG":
	    pass
	    # TODO this is where the restricted unauthenticated stuff gets done (you can only log in and register)
	    #	but I guess really we'll just forward all the messages to and from NickServ or else give the error
	else:
	    return self.send(":%s %03d :You have not registered\r\n" % (self.host, IRCMsg.ERR_NOTREGISTERED))

    def _dispatch_user(self, msg):
	# NOTE: We can assume self.user is set correctly because it's checked in _dispatch
	if msg.cmd == "PRIVMSG":
	    if not self.user:
		return self.send(":%s NOTICE %s :You aren't logged in yet\r\n" % (self.host, self.nick))
	    elif not msg.text:
		return self.send(":%s %03d :No text to send\r\n" % (self.host, IRCMsg.ERR_NOTEXTTOSEND))
	    else:
		if msg.args[0][0] == '#':
		    channel = Channel.get(msg.args[0])
		else:
		    channel = User.get(msg.args[0])

		if not channel:
		    return self.send(":%s %03d %s :Cannot send to channel\r\n" % (self.host, IRCMsg.ERR_CANNOTSENDTOCHAN, msg.args[0]))
		elif msg.text[0] == '.':
		    self.user.do_command(msg.text[1:])
		elif msg.text[0] == '\x01':
		    # TODO process ctcp messages
		    pass
		else:
		    channel.do_say(user, msg.text)
	elif msg.cmd == "MODE":
	    channel = Channel.get(msg.args[0])
	    if channel:
		if len(msg.args) > 1 and 'b' in msg.args[1]:
		    return self.send(":%s %03d %s %s :End of channel ban list\r\n" % (self.host, IRCMsg.RPL_ENDOFBANLIST, self.nick, msg.args[0]))
		# TODO do channel mode command processing
		return self.send(":%s %03d %s %s %s\r\n" % (self.host, IRCMsg.RPL_CHANNELMODEIS, self.nick, msg.args[0], channel.mode))
	    else:
		if not msg.args[0] == self.nick:
		    return self.send(":%s %03d :Cannot change mode for other users\r\n" % (self.host, IRCMsg.ERR_USERSDONTMATCH))
		# TODO check for unknown mode flag
		#return self.send(":%s %03d :Unknown MODE flag\r\n" % (self.host, IRCMsg.ERR_UMODEUNKNOWNFLAG))
		# TODO the +i here is just to send something back and should be removed later when properly implemented
		# TODO the +i is stored in user (since it's so easy now to do that)
		return self.send(":%s %03d %s %s\r\n" % (self.host, IRCMsg.RPL_UMODEIS, msg.args[0], self.user.mode))
	elif msg.cmd == "JOIN":
	    if msg.args[0] == '0':
		# TODO leave all channels
		pass
	    else:
		for name in msg.args[0].split(','):
		    if not self.user.join(name):
			self.send(":%s %03d %s :No such channel\r\n" % (self.host, IRCMsg.ERR_NOSUCHCHANNEL, name))
	elif msg.cmd == "PART":
	    for name in msg.args[0].split(','):
		if not self.user.leave(name):
		    self.send(":%s %03d %s :No such channel\r\n" % (self.host, IRCMsg.ERR_NOSUCHCHANNEL, name))
	elif msg.cmd == "NAMES":
	    #if (msg->m_numparams > 1 && !strcmp(msg->m_params[1], self.host))
	    #	return self.send(":%s %03d %s :No such server\r\n" % (self.host, IRCMsg.ERR_NOSUCHSERVER, msg.args[1]))
	    for name in msg.args[0].split(','):
		self._send_names(name)
	elif msg.cmd == "WHOIS":
	    # TODO do rest of whois
	    return self.send(":%s %03d %s :End of WHOIS list\r\n" % (self.host, IRCMsg.RPL_ENDOFWHOIS, self.nick))
	elif msg.cmd == "QUIT":
	    if self.user:
		# TODO quit all channels
		pass
	    self.close()
	    return
	elif msg.cmd == "WHO":
	    if msg.nargs > 1 and msg.args[1] == self.host:
		return self.send(":%s %03d %s :No such server\r\n" % (self.host, IRCMsg.ERR_NOSUCHSERVER, msg.args[1]))
	    # TODO finish this
	    self._send_who(msg.args[0])
	elif msg.cmd == "LIST":
	    if msg.nargs > 1 and msg.args[1] == self.host:
		return self.send(":%s %03d %s :No such server\r\n" % (self.host, IRCMsg.ERR_NOSUCHSERVER, msg.args[1]))
	    # TODO cycle through comma-seperated list of channels
	    self._send_list(msg.args[0])
	elif msg.cmd == "PASS" or msg.cmd == "USER":
	    return self.send(":%s %03d :Unauthorized command (already registered)\r\n" % (self.host, IRCMsg.ERR_ALREADYREGISTERED))
	else:
	    return self.send(":%s %03d %s :Unknown Command\r\n" % (self.host, IRCMsg.ERR_UNKNOWNCOMMAND, msg.args[0]))

    def _login(self):
	if not self.nick:
	    self.close("No nick given")
	    return
	user = User.get(self.nick)
	if user:
	    if user.connected():
		return self.send(":%s %03d %s :Nickname is already in use\r\n" % (self.host, IRCMsg.ERR_NICKNAMEINUSE, self.nick))
	    elif not self.password:
		self.close("Password required for %s" % (self.nick,))
		return
	    else:
		self.user = User.login(self.nick, self.password)
		if not self.user:
		    self.close("Invalid password for %s\r\n" % (self.nick,))
		    return
	else:
	    self.send(":%s NOTICE %s :That nick is not registered. Using guest account.\r\n" % (self.host, self.nick))
	    self.user = User.get_guest()
	if self.user:
	    self.user.do_connect(self)
	self.send(":%s %03d %s :Welcome to the Moo IRC Portal %s!~%s@%s\r\n" % (self.host, IRCMsg.RPL_WELCOME, self.nick, self.nick, self.nick, self.addr))
	self.send(":%s %03d %s :Your host is %s, running version SuperDuperMoo v%s\r\n" % (self.host, IRCMsg.RPL_YOURHOST, self.nick, self.host, self.version))
	self.send(":%s %03d %s :This server was created ???\r\n" % (self.host, IRCMsg.RPL_CREATED, self.nick))
	self.send(":%s %03d %s :%s SuperDuperMoo v%s ? ?\r\n" % (self.host, IRCMsg.RPL_MYINFO, self.nick, self.host, self.version))
	# TODO you can send the 005 ISUPPORT messages as well (which doesn't appear to be defined in the IRC standard)
	self._send_motd();
	self.send(":TheRealm!realm@%s NOTICE %s :Welcome to The Realm of the Jabberwock, %s\r\n" % (self.host, self.nick, self.nick))

    def _send_motd(self):
	self.send(":%s %03d %s :- %s Message of the Day -\r\n" % (self.host, IRCMsg.RPL_MOTDSTART, self.nick, self.host))
	# TODO read in motd from somewhere and print it
	self.send(":%s %03d %s :End of /MOTD command.\r\n" % (self.host, IRCMsg.RPL_ENDOFMOTD, self.nick))

    def _send_names(self, channel_name):
	# TODO we need some way to check if the room we are currently in cannot list members (you don't want to list members if you
	#	are in the cryolocker, for example)
	list = ''
	channel = Channel.get(channel_name)
	for thing in channel.users:
	    # TODO we should check that things are invisible, and also add @ for wizards or something
	    list = list + thing.name + ' '
	self.send(":%s %03d %s = %s :%s\r\n" % (self.host, IRCMsg.RPL_NAMREPLY, self.nick, channel_name, list.rstrip()))
	self.send(":%s %03d %s %s :End of NAMES list.\r\n" % (self.host, IRCMsg.RPL_ENDOFNAMES, self.nick, channel_name))

    def _send_who(self, mask):
	# TODO should you make this do more than just list channels? (like work with users and stuff as well)
	"""
	channel = MooThing::get_channel(mask);
	if (channel) {
		// TODO we need some way to check if the room we are currently in cannot list members (you don't want to list members if you
		//	are in the cryolocker, for example)
		if ((users = dynamic_cast<MooObjectArray *>(channel->resolve_property("users")))) {
			for (int i = 0; i <= users->last(); i++) {
				cur = users->get(i);
				// TODO we should check that things are invisible, and also add @ for wizards or something
				if ((cur = cur->resolve_property("name")) && (thing_name = cur->get_string())) {
					IRCMsg::send(driver, ":%s %03d %s %s %s %s %s %s H :0 %s\r\n", server_name, IRC_RPL_WHOREPLY, nick, mask, thing_name, server_name, server_name, thing_name, thing_name);
				}
			}
		}
	}
	"""
	self.send(":%s %03d %s %s :End of WHO list.\r\n" % (self.host, IRCMsg.RPL_ENDOFWHO, self.nick, mask))

    def _send_list(self, name):
	# TODO accessing the db directly isn't really correct here, we should either call a method, evaluate direct code (but which
	#	would allow easy use of a method on chanserv), or something to put the actual db access into a method on ChanServ
	"""
	if ((channels = frame->resolve("ChanServ"))) {
		if ((list = dynamic_cast<MooObjectHash *>(channels->resolve_property("db")))) {
			list->reset();
			while ((cur = list->next())) {
				if ((obj = cur->resolve_property("name")) && (str = obj->get_string()))
					IRCMsg::send(driver, ":%s %03d %s %s 1 :\r\n", server_name, IRC_RPL_LIST, nick, str);
			}
		}
	}
	"""
	self.send(":%s %03d %s :End of LIST.\r\n" % (self.host, IRCMsg.RPL_ENDOFLIST, self.nick))

    @staticmethod
    def do_connection_thread(self, addr):
	while 1:
	    try:
		msg = self.readmsg()
		Thing.lock_all()
		self._dispatch(msg)
	    except socket.error, e:
		print "Socket Error: " + e
		Thing.unlock_all()
		break
	    except:
		t = traceback.format_exc()
		for text in t.split('\n'):
		    self.send(":%s NOTICE %s :%s\r\n" % (self.host, self.nick, text))
	    Thing.unlock_all()
	self.close()




 
