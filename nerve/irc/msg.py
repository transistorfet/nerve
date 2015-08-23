#!/usr/bin/python3
# -*- coding: utf-8 -*-


class Colours (object):
    black = '\x031'
    blue = '\x032'
    green = '\x033'
    red = '\x034'
    brown = '\x035'
    purple = '\x036'
    darkyellow = '\x037'
    yellow = '\x038'
    lightgreen = '\x039'
    teal = '\x0310'
    aqua = '\x0311'
    brightblue = '\x0312'
    fucia = '\x0313'
    grey = '\x0314'
    lightgrey = '\x0315'
    white = '\x0316'


class MsgType (object):
    RPL_WELCOME =             1
    RPL_YOURHOST =            2
    RPL_CREATED =             3
    RPL_MYINFO =              4
    RPL_BOUNCE =              5
    
    RPL_TRACELINK =         200
    RPL_TRACECONNECTING =   201
    RPL_TRACEHANDSHAKE =    202
    RPL_TRACEUNKNOWN =      203
    RPL_TRACEOPERATOR =     204
    RPL_TRACEUSER =         205
    RPL_TRACESERVER =       206
    RPL_TRACESERVICE =      207
    RPL_TRACENEWTYPE =      208
    RPL_TRACECLASS =        209
    RPL_TRACERECONNECT =    210
    RPL_STATSLINKINFO =     211
    RPL_STATSCOMMANDS =     212
    RPL_ENDOFSTATS =        219
    RPL_UMODEIS =           221
    RPL_SERVLIST =          234
    RPL_SERVLISTEND =       235
    RPL_STATSUPTIME =       242
    RPL_STATSOLINE =        243
    RPL_LUSERCLIENT =       251
    RPL_LUSEROP =           252
    RPL_LUSERUNKNOWN =      253
    RPL_LUSERCHANNELS =     254
    RPL_LUSERME =           255
    RPL_ADMINME =           256
    RPL_ADMINLOC1 =         257
    RPL_ADMINLOC2 =         258
    RPL_ADMINEMAIL =        259
    RPL_TRYAGAIN =          263
    RPL_TRACELOG =          261
    RPL_TRACEEND =          262
    
    RPL_AWAY =              301
    RPL_USERHOST =          302
    RPL_ISON =              303
    RPL_UNAWAY =            305
    RPL_NOAWAY =            306
    RPL_WHOISUSER =         311
    RPL_WHOISSERVER =       312
    RPL_WHOISOPERATOR =     313
    RPL_WHOWASUSER =        314
    RPL_ENDOFWHO =          315
    RPL_WHOISIDLE =         317
    RPL_ENDOFWHOIS =        318
    RPL_WHOISCHANNELS =     319
    RPL_WHOISSPECIAL =      320
    RPL_LISTSTART =         321
    RPL_LIST =              322
    RPL_ENDOFLIST =         323
    RPL_CHANNELMODEIS =     324
    RPL_UNIQOPIS =          325
    RPL_NOTOPIC =           331
    RPL_TOPIC =             332
    RPL_INVITING =          341
    RPL_SUMMONING =         342
    RPL_INVITELIST =        346
    RPL_ENDOFINVITELIST =   347
    RPL_EXCEPTLIST =        348
    RPL_ENDOFEXCEPTLIST =   349
    RPL_VERSION =           351
    RPL_WHOREPLY =          352
    RPL_NAMREPLY =          353
    RPL_LINKS =             364
    RPL_ENDOFLINKS =        365
    RPL_ENDOFNAMES =        366
    RPL_BANLIST =           367
    RPL_ENDOFBANLIST =      368
    RPL_ENDOFWHOWAS =       369
    RPL_INFO =              371
    RPL_MOTD =              372
    RPL_ENDOFINFO =         374
    RPL_MOTDSTART =         375
    RPL_ENDOFMOTD =         376
    RPL_YOUREOPER =         381
    RPL_REHASHING =         382
    RPL_YOURESERVICE =      383
    RPL_TIME =              391
    RPL_USERSSTART =        392
    RPL_USERS =             393
    RPL_ENDOFUSERS =        394
    RPL_NOUSERS =           395
    
    ERR_NOSUCHNICK =        401
    ERR_NOSUCHSERVER =      402
    ERR_NOSUCHCHANNEL =     403
    ERR_CANNOTSENDTOCHAN =  404
    ERR_TOOMANYCHANNELS =   405
    ERR_WASNOSUCHNICK =     406
    ERR_TOOMANYTARGETS =    407
    ERR_NOSUCHSERVICE =     408
    ERR_NOORIGIN =          409
    ERR_NORECIPIENT =       411
    ERR_NOTEXTTOSEND =      412
    ERR_NOTOPLEVEL =        413
    ERR_WILDTOPLEVEL =      414
    ERR_BADMASK =           415
    ERR_UNKNOWNCOMMAND =    421
    ERR_NOMOTD =            422
    ERR_NOADMININFO =       423
    ERR_FILEERROR =         424
    ERR_NONICKNAMEGIVEN =   431
    ERR_ERRONEUSNICKNAME =  432
    ERR_NICKNAMEINUSE =     433
    ERR_NICKCOLLISION =     436
    ERR_UNAVAILRESOURCE =   437
    ERR_USERNOTINCHANNEL =  441
    ERR_NOTONCHANNEL =      442
    ERR_USERONCHANNEL =     443
    ERR_NOLOGIN =           444
    ERR_SUMMONDISABLED =    445
    ERR_USERDISABLED =      446
    ERR_NOTREGISTERED =     451
    ERR_NEEDMOREPARAMS =    461
    ERR_ALREADYREGISTERED = 462
    ERR_NOPERMFORHOST =     463
    ERR_PASSWDMISMATCH =    464
    ERR_YOUREBANNEDCREEP =  465
    ERR_YOUWILLBEBANNED =   466
    ERR_KEYSET =            467
    ERR_CHANNELISFULL =     471
    ERR_UNKNOWNMODE =       472
    ERR_INVITEONLYCHAN =    473
    ERR_BANNEDFROMCHAN =    474
    ERR_BADCHANNELKEY =     475
    ERR_BADCHANMASK =       476
    ERR_NOCHANMODES =       477
    ERR_BANLISTFULL =       478
    ERR_NOPRIVILEGES =      481
    ERR_CHANOPRIVSNEEDED =  482
    ERR_CANTKILLSERVER =    483
    ERR_RESTRICTED =        484
    ERR_UNIQOPPRIVSNEEDED = 485
    ERR_NOOPERHOST =        491
    ERR_UMODEUNKNOWNFLAG =  501
    ERR_USERSDONTMATCH =    502

    cmdlist = {
        "PASS" : (0, 1, 1),
        "NICK" : (0, 0, 1),
        "USER" : (1, 4, 4),
        "OPER" : (0, 2, 2),
        "QUIT" : (1, 0, 1),
        "SQUIT" : (1, 2, 2),
        "JOIN" : (0, 1, 2),
        "PART" : (1, 1, 2),
        "MODE" : (0, 1, 0),
        "TOPIC" : (1, 1, 2),
        "NAMES" : (0, 0, 2),
        "LIST" : (0, 0, 2),
        "INVITE" : (0, 2, 2),
        "KICK" : (1, 2, 3),
        "PRIVMSG" : (1, 0, 2),
        "NOTICE" : (1, 0, 2),
        "MOTD" : (0, 0, 1),
        "LUSERS" : (0, 0, 2),
        "VERSION" : (0, 0, 1),
        "STATS" : (0, 0, 2),
        "LINKS" : (0, 0, 2),
        "TIME" : (0, 0, 1),
        "CONNECT" : (0, 2, 3),
        "TRACE" : (0, 0, 1),
        "ADMIN" : (0, 0, 1),
        "INFO" : (0, 0, 1),
        "SERVLIST" : (0, 0, 2),
        "SQUERY" : (1, 0, 2),
        "WHO" : (0, 0, 2),
        "WHOIS" : (0, 0, 2),
        "WHOWAS" : (0, 0, 3),
        "KILL" : (1, 2, 2),
        "PING" : (1, 0, 2),
        "PONG" : (1, 0, 2),
        "ERROR" : (1, 1, 1),
    }

    @classmethod
    def cmdinfo(cls, cmd):
        return cls.cmdlist.get(cmd)


class Msg (object):
    def __init__(self, line=None):
        self.clear()
        if line:
            self.unmarshal(line)

    def clear(self):
        self.nick = None
        self.hostname = None
        self.cmd = ''
        self.args = [ ]
        self.nargs = 0
        self.text = ''

    def unmarshal(self, line):
        remain = line
        if remain[0] == ':':
            (ident, remain) = remain.split(None, 1)
            if ident.find('!') >= 0:
                (self.nick, self.hostname) = ident[1:].split('!')
            else:
                self.hostname = ident[1:]
        parts = remain.split(None, 1)
        self.cmd = parts[0]
        if len(parts) > 1:
            parts = parts[1].split(':', 1)
            self.args = parts[0].split()
            if len(parts) > 1:
                self.args.append(parts[1])
                cmdinfo = MsgType.cmdinfo(self.cmd)
                if cmdinfo and cmdinfo[0]:
                    self.text = self.args[-1]
        self.nargs = len(self.args)
        self.line = line
        #print line
        #print self.args
        #print "%s %s  %s %s" % (self.nick, self.hostname, self.cmd, self.text)

    def needs_more_params(self):
        cmdinfo = MsgType.cmdinfo(self.cmd)
        if cmdinfo and self.nargs < cmdinfo[1]:
            return 1
        return 0

 
