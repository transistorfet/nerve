#!/usr/bin/python
# -*- coding: utf-8 -*-

from .devices import MediaLib, Playlist
from .updater import MediaUpdaterTask
from .youtube import YoutubePlaylistFetcher

from .controllers import MediaLibController


def init():
    # TODO if we have an init like this, we can do stuff when the module is loaded...
    # but what about having multiple instances... multiple nodes inside a single process. Is this even worth thinking about

    # you could start the updater threads here, but that would assume there's only one medialib in the system... shouldn't
    # it at least be possible to have more? (i mean generallly, for other devices in other modules)

    # would you register a single controller for the module?  would you register several? or would it auto load based on a controller dir?
    # would you register the device types, so that they can be created through the config data?
    #nerve.register_device_type('medialib', MediaLib, 'Media Library Database')


    #nerve.register_server_type('http', HTTPServer, "HTTP Server")
    #nerve.register_controller('medialib', MediaLibController)
    pass

