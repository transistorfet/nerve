#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

from .devices import GstreamerPipeline


class GObjectThread (nerve.Thread):
    def __init__(self):
        super().__init__(name='GobjectThread')

        GObject.threads_init()
        Gst.init(None)
        self.loop = GObject.MainLoop()

    def run(self):
        try:
            self.loop.run()
        except KeyboardInterrupt:
            nerve.quit()

    def stop(self):
        if GstreamerPipeline.singleton:
            GstreamerPipeline.singleton.quit()
        self.loop.quit() 


