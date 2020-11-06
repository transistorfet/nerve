#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .playlists import Playlist
from .devices import MediaLibDevice
from .controllers import MediaLibController

def init():
    # would you register a single controller for the module?  would you register several? or would it auto load based on a controller dir?
    # would you register the device types, so that they can be created through the config data?
    #nerve.register_device_type('medialib', MediaLibDevice, 'Media Library Database')

    #nerve.register_server_type('http', HTTPServer, "HTTP Server")
    #nerve.register_controller('medialib', MediaLibController)

    #nerve.query('devices/components/register', 'MediaLib', 'nerve/medialib/assets/js/components.js')
    import nerve.mithril
    nerve.mithril.register_js('MediaLib', 'nerve/medialib/assets/js/components.js')
    nerve.mithril.register_css('nerve/medialib/assets/css/medialib.css')

import nerve.modules

class Module (nerve.modules.Module):
    def __init__(self, **config):
        super().__init__(**config)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('medialib_dirs', 'Directories', default=list(), itemtype='str')
        config_info.add_setting('youtube_playlists', 'YouTube Playlists', default=list(), itemtype='str')
        return config_info

    def update_config_data(self, config):
        super().update_config_data(config)

