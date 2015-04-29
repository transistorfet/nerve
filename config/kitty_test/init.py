#!/usr/bin/python3
# -*- coding: utf-8 -*-

#import nerve

#nerve.set_object('/devices/player', 'xmms2.Xmms2')
#nerve.set_object('/devices/player', 'vlc.VLCHTTP')
#nerve.set_object('/devices/layout', 'layout.LayoutDevice')
#nerve.set_object('/devices/deskclock', 'deskclock.Deskclock', "/dev/ttyACM0", 19200)
#nerve.set_object('/devices/player', 'vlc.VLCHTTP')
#nerve.set_object('/devices/medialib', 'medialib/MediaLib')


"""
class Test (nerve.Device):
    def __init__(self):
        nerve.Device.__init__(self)

    def say(self, text):
        print(text)

    def toggle(self):
        return 50

#nerve.set_object('/devices/test', Test())
nerve.set_object('/devices/testthing', Test())
"""


"""
nerve.add_server('http', 'http.HTTPServer', 8888)
nerve.add_controller('http', 'query', QueryController())
nerve.add_controller('http', 'files', FileController("nerve/http/wwwdata"))
nerve.add_controller('http', 'medialib', MediaLibController())
"""


#rgb = nerve.set_object('/devices/rgb', 'serial/NerveSerialDevice', **dict(file="/dev/ttyACM1", baud=19200))

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



class SpecialEvent (nerve.Event):
    def __init__(self, **config):
        config['repeat'] = 1.0
        super().__init__(**config)
        self.high = False

    def run(self):
        temp = nerve.query("http://192.168.1.180:8888/query/sensors/temp0")
        if not self.high and float(temp) > 24:
            self.high = True
            print("HEY IT HAPPENED")

        if self.high and float(temp) < 23:
            self.high = False
            print("IT'S NOT HAPPENING")

#nerve.set_object("/devices/thing/special", SpecialEvent())



