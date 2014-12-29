#!/usr/bin/python
# -*- coding: utf-8 -*-

#import nerve

#nerve.add_device('player', 'xmms2.Xmms2')
#nerve.add_device('player', 'vlc.VLCHTTP')
#nerve.add_device('layout', 'layout.LayoutDevice')
#nerve.add_device('deskclock', 'deskclock.Deskclock', "/dev/ttyACM0", 19200)
#nerve.add_device('player', 'vlc.VLCHTTP')
#nerve.add_device('medialib', 'medialib/MediaLib')

"""
class Test (nerve.Device):
    def __init__(self):
	nerve.Device.__init__(self)

    def say(self, text):
	print text

    def toggle(self):
	return 50

nerve.mainloops[0].root.player = Test()
"""

"""
class Change (nerve.Device):
    def test(self, **kwargs):
	server = nerve.get_server('base/Console')
	server.config['poop'] = "a thing"
	print server.config
	return nerve.get_config('base/Console')

    def test2(self, **kwargs):
	server = nerve.get_server('base/Console')
	server.config['poop2'] = "a thing"
	return nerve.get_config('base/Console')

    def save(self):
	nerve.save_config()

nerve.add_device('change', Change())
"""


"""
nerve.add_server('http', 'http.HTTPServer', 8888)
nerve.add_controller('http', 'query', QueryController())
nerve.add_controller('http', 'files', FileController("nerve/http/wwwdata"))
nerve.add_controller('http', 'medialib', MediaLibController())
"""

#nerve.add_portal('raw.UDPServer', 5960)
#nerve.add_portal('raw.TCPServer', 5960)
#nerve.add_portal('http.HTTPServer', 8888)
#nerve.add_portal('raw.Console')
#nerve.add_server('console', 'base/Console')

#rgb = nerve.add_device('rgb', 'serial/NerveSerialDevice', **dict(file="/dev/ttyACM1", baud=19200))

config = {
    'devices' : [
	[ 'player', 'xmms2.Xmms2' ],
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

{
    'devices' : [
	{ 'device' : 'xmms2.Xmms2', 'node' : 'player' },
	{ 'device' : 'deskclock.Deskclock', 'node' : 'deskclock', 'devfile' : '/dev/ttyACM0', 'baud' : 19200 },
    ]
}

{
    # TODO is this how we should do this??? loading these would only cause them to register their server, controller, and device types
    'modules' : [ 'http', 'base', 'medialib', 'player', 'vlc' ],

    'servers' : {
	'http' : {
	    'type' : 'http/HTTPServer',
	    'port' : 8888,
	    'controllers' : {
		'__default__' : {
		    'type' : 'base/RedirectController',
		    'target' : '/files/index.php'
		},
		'files' : {
		    'type' : 'http/FileController',
		    'root' : "nerve/http/wwwdata"
		},
		'medialib' : {
		    'type' : 'medialib/MediaLibController',
		    'device' : 'medialib'
		},
		'query' : {
		    'type' : 'base/QueryController'
		}
	    }
	},
	'console' : {
	    'type' : 'raw/Console',
	    'controllers' : {
		'__default__' : {
		    'type' : 'base/QueryController'
		}
	    }
	},
	'udp' : {
	    'type' : 'raw/UDPServer',
	    'port' : 5959,
	    'controllers' : {
		'__default__' : {
		    'type' : 'base/QueryController'
		}
	    }
	}
    },
    'devices' : {
	'medialib' : {
	    'type' : 'medialib/MediaLib',
	    'update_path' : [ '/media/media/Music', 'media/media/Torrents' ]
	},
	'deskclock' : {
	    'type' : 'DeskClock',
	    'devfile' : '/dev/ttyACM0',
	    'baud' : 19200
	},
	'rgb' : {
	    'type' : 'serial/NerveSerialDevice',
	    'devfile' : '/dev/ttyACM1',
	    'baud' : 19200
	},
	'tv' : {
	    'type' : 'TV',
	    'parent' : 'rgb'
	},
	'stereo' : {
	    'type' : 'stereo',
	    'parent' : 'rgb'
	}
    }
}

