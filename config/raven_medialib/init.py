#!/usr/bin/python
# -*- coding: utf-8 -*-

#import nerve

#nerve.add_device('player', 'xmms2.Xmms2')
#nerve.add_device('player', 'vlc.VLCHTTP')
#nerve.add_device('layout', 'layout.LayoutDevice')
#nerve.add_device('deskclock', 'deskclock.Deskclock', "/dev/ttyACM0", 19200)
#nerve.add_device('player', 'vlc.VLCHTTP')
nerve.add_device('medialib', 'medialib.MediaLib')

#nerve.add_portal('raw.UDPServer', 5960)
#nerve.add_portal('raw.TCPServer', 5960)
nerve.add_portal('http.HTTPServer', 8888)
nerve.add_portal('raw.Console')


