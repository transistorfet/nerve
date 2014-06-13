#!/usr/bin/python
# -*- coding: utf-8 -*-

#import nerve

#nerve.add_device('music', 'xmms2.Xmms2')
#nerve.add_device('music', 'vlchttp.VLCHTTP')
nerve.add_device('layout', 'layout.LayoutDevice')
#nerve.add_device('deskclock', 'deskclock.Deskclock', "/dev/ttyACM0", 19200)
#nerve.add_device('player', 'vlchttp.VLCHTTP')
nerve.add_device('medialib', 'medialib.MediaLib')

#nerve.add_portal('udpserver.UDPServer', 5960)
nerve.add_portal('tcpserver.TCPServer', 5960)
nerve.add_portal('httpserver.HTTPServer', 8888)
nerve.add_portal('console.Console')

config = {
    'devices' : [
	[ 'music', 'xmms2.Xmms2' ],
	[ 'deskclock', 'deskclock.Deskclock' ],
	[ 'rgb', 'serialdev.NerveSerialDevice' ],
	[ 'deskclockold', 'serialdev.SerialDevice' ]
    ],
    'portals' : [
	'tcpserver.TCPServer',
	'httpserver.HTTPServer',
	'console.Console'
    ],
    'tcpserver' : { 'port' : 5960 },
    'httpserver' : { 'port' : 8999 },
    'deskclock' : { 'devfile' : '/dev/ttyACM0', 'baud' : 19200 },
    'rgb' : { 'devfile' : '/dev/ttyACM1', 'baud' : 19200 },
    'deskclockold' : { 'devfile' : '/dev/ttyACM0', 'baud' : 19200 }
}

