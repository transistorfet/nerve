#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .playlists import Playlist
from .devices import MediaLibDevice
from .controllers import MediaLibController
from .tasks import MediaLibUpdater

updater_task = None

def init():
    # TODO if we have an init like this, we can do stuff when the module is loaded...
    # but what about having multiple instances... multiple nodes inside a single process. Is this even worth thinking about

    # you could start the updater threads here, but that would assume there's only one medialib in the system... shouldn't
    # it at least be possible to have more? (i mean generallly, for other devices in other modules)

    # would you register a single controller for the module?  would you register several? or would it auto load based on a controller dir?
    # would you register the device types, so that they can be created through the config data?
    #nerve.register_device_type('medialib', MediaLibDevice, 'Media Library Database')


    #nerve.register_server_type('http', HTTPServer, "HTTP Server")
    #nerve.register_controller('medialib', MediaLibController)

    from .tasks import MediaLibUpdaterTask

    from .updaters.files import MediaFilesUpdater
    from .updaters.youtube import YoutubePlaylistUpdater

    global updater_task
    updater_task = MediaLibUpdaterTask()
    updater_task.add('files', MediaFilesUpdater())
    updater_task.add('youtube', YoutubePlaylistUpdater())

    updater_task.start()

def get_config_info(config_info):
    config_info.add_setting('medialib_dirs', 'Directories', default=list(), itemtype='str')
    config_info.add_setting('youtube_playlists', 'YouTube Playlists', default=list(), itemtype='str')
    return config_info

def run_updater():
    updater_task.run_updater()



