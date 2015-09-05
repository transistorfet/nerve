#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.medialib

import os
import sys
import urllib
import subprocess

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GstVideo
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkX11


class GstreamerPlayer (nerve.Device):
    def __init__(self, **config):
        self.pipeline = GstreamerPipeline()
        super().__init__(**config)

        self.title = ""
        self.current_song = ""
        self.reply = None

        #self.pipeline.set_uri("file:///home/trans/Downloads/3 Teeth - Nihil.mp4")
        #self.pipeline.set_uri("file:///home/trans/Downloads/GoaTrance.mp3")
        #self.pipeline.set_uri("file:///home/trans/Downloads/60-test-german_coast_guard.mpg")
        #self.pipeline.set_uri("file:///home/trans/Downloads/104-Lamb-Piste_6.mp3")
        #self.pipeline.play()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('visualization', "Visualization", default='libvisual_corona')
        #for option in servers.keys():
        config_info.add_option('visualization', 'libvisual_jess', 'libvisual_jess')
        config_info.add_option('visualization', 'libvisual_bumpscope', 'libvisual_bumpscope')
        config_info.add_option('visualization', 'libvisual_corona', 'libvisual_corona')
        config_info.add_option('visualization', 'libvisual_infinite', 'libvisual_infinite')
        config_info.add_option('visualization', 'libvisual_jakdaw', 'libvisual_jakdaw')
        config_info.add_option('visualization', 'libvisual_lv_analyzer', 'libvisual_lv_analyzer')
        config_info.add_option('visualization', 'libvisual_lv_scope', 'libvisual_lv_scope')
        config_info.add_option('visualization', 'libvisual_oinksie', 'libvisual_oinksie')
        config_info.add_option('visualization', 'spacescope', 'spacescope')
        config_info.add_option('visualization', 'spectrascope', 'spectrascope')
        config_info.add_option('visualization', 'synaescope', 'synaescope')
        config_info.add_option('visualization', 'wavescope', 'wavescope')
        return config_info

    def update_config_data(self, data):
        super().update_config_data(data)
        self.pipeline.set_visualization(self.get_setting('visualization'))

    def toggle(self):
        self.pipeline.toggle_playpause()

    def next(self):
        os.system("xmms2 next")
        self.update_info()

    def previous(self):
        os.system("xmms2 prev")
        self.update_info()

    def fullscreen(self):
        self.pipeline.fullscreen_toggle(None)

    def play(self, url):
        pass

    def enqueue(self, url):
        pass

    def getsong(self):
        self.update_info()
        return self.current_song

    def update_info(self):
        proc = subprocess.Popen(["xmms2", "current"], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        parts = out.decode('utf-8').split(': ', 2)
        self.current_song = parts[1]
        (self.artist, _, self.title) = self.current_song.partition(" - ")

    def load_playlist(self, name):
        self.pipeline.stop()
        self.pipeline.queue = [ ]

        for media in nerve.medialib.Playlist(name).get_list():
            nerve.log("adding to playlist: " + media['artist'] + " - " + media['title'] + " (" + media['filename'] + ")")
            self.pipeline.queue.append(media['filename'])
        self.pipeline.play()


class GstreamerPipeline (object):
    singleton = None

    def __new__(cls):
        if not cls.singleton:
            cls.singleton = super().__new__(cls)
        return cls.singleton

    def __init__(self, visualization=None):
        self.queue = [ ]

        self.fullscreen = False
        self.fullscreen_hide_pointer_id = None

        self.window = Gtk.Window()
        #self.window.connect("delete-event", Gtk.main_quit)
        self.window.connect("delete-event", nerve.quit)
        self.window.connect("key-release-event", self.on_key_release)
        self.window.connect("button-press-event", self.on_mouse_click)
        self.window.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.window.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color(0, 0, 0))
        self.window.resize(640, 480)
        self.window.show_all()

        self.pipeline = Gst.ElementFactory.make('playbin')
        self.pipeline.set_property('force-aspect-ratio', True)

        self.set_visualization(visualization)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.enable_sync_message_emission()
        self.bus.connect("sync-message::element", self.sync_handler)
        self.bus.connect("message", self.message_handler)
        self.pipeline.connect("about-to-finish", self.about_to_finish_handler)

    def set_visualization(self, name):
        playing = self.is_playing()
        self.stop()
        if not name:
            self.pipeline.set_property('vis-plugin', None)
        else:
            self.visualization = Gst.ElementFactory.make(name)
            self.pipeline.set_property('flags', self.pipeline.get_property('flags') | 0x00000008)
            self.pipeline.set_property('vis-plugin', self.visualization)
        if playing:
            self.play()

    def set_uri(self, uri):
        self.pipeline.set_property('uri', uri)

    def toggle_playpause(self):
        if self.is_playing():
            self.pause()
        else:
            self.play()

    def play(self):
        self.change_state(Gst.State.PLAYING)

    def pause(self):
        self.change_state(Gst.State.PAUSED)

    def stop(self):
        self.change_state(Gst.State.READY)

    def quit(self):
        self.change_state(Gst.State.NULL)

    def change_state(self, target_state):
        self.pipeline.set_state(target_state)
        (statechange, state, pending) = self.pipeline.get_state(timeout=5 * Gst.SECOND)
        if statechange != Gst.StateChangeReturn.SUCCESS:
            nerve.log("gstreamer failed waiting for state change to " + str(pending))
            return False
        return True

    def is_playing(self):
        (change, state, pending) = self.pipeline.get_state(0)
        if state == Gst.State.PLAYING:
            return True
        return False

    # sync handler (assigns video sink to drawing area)
    def sync_handler(self, bus, message):
        if message.get_structure() is None:
            return Gst.BusSyncReply.PASS
        if message.get_structure().get_name() == 'prepare-window-handle':
            message.src.set_window_handle(self.window.get_window().get_xid())
        return Gst.BusSyncReply.PASS

    # message handler (handles gstreamer messages posted to the bus)
    def message_handler(self, bus, message):
        if message.type == Gst.MessageType.STATE_CHANGED:
            oldstate, newstate, pending = message.parse_state_changed()
            """
            if message.src == self.pipeline:
                nerve.log("State Changed to " + str(newstate))
                if newstate == Gst.State.PLAYING:
                    self.is_playing.set()
                else:
                    self.is_playing.clear()
            """

        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            nerve.log("gstreamer error: %s, %s, %s" % (err, debug, err.code))
            #self.pipeline.set_state(Gst.State.READY)
            #self.player.request_update.set()

        elif message.type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            nerve.log("gstreamer warning: %s, %s, %s" % (err, debug, err.code))

        elif message.type == Gst.MessageType.INFO:
            err, debug = message.parse_info()
            nerve.log("gstreamer info: %s, %s, %s" % (err, debug, err.code))

        elif message.type == Gst.MessageType.BUFFERING:
            print("Buffering Issue")
            #percent = message.parse_buffering()
            #if percent < 100:
            #    self.pipeline.set_state(Gst.State.PAUSED)
            #else:
            #    self.pipeline.set_state(Gst.State.PLAYING)

        elif message.type == Gst.MessageType.EOS:
            nerve.log("player received end of stream signal")
            #self.player.request_update.set()

    def about_to_finish_handler(self, message):
        print("About to finish")

    def on_key_release(self, widget, event, data=None):
        if event.keyval == Gdk.KEY_Escape:
            if self.fullscreen == True:
                self.fullscreen_toggle(None)
        elif event.keyval == Gdk.KEY_F or event.keyval == Gdk.KEY_f:
            self.fullscreen_toggle(None)

    def on_mouse_click(self, widget, event, data=None):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            self.toggle_playpause()

    def fullscreen_toggle(self, widget):
        if self.fullscreen == False:
            self.window.fullscreen()
            self.fullscreen = True
            self.fullscreen_hide_pointer_id = GObject.timeout_add(1000, self.fullscreen_hide_pointer)
        else:
            self.window.unfullscreen()
            self.fullscreen = False
            self.fullscreen_show_pointer()

    def fullscreen_show_pointer(self):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.window.get_root_window().set_cursor(cursor)

    def fullscreen_hide_pointer(self):
        if self.fullscreen != True:
            return
        cursor = Gdk.Cursor.new(Gdk.CursorType.BLANK_CURSOR)
        self.window.get_root_window().set_cursor(cursor)
        self.fullscreen_hide_pointer_id = None
        return False  # GObject.timeout_add for pointer show/hide on fullscreen, using return false to avoid repeated calls.

    def pointer_position_watch(self, widget, event):
        if self.fullscreen == False:
            return

        if self.fullscreen_hide_pointer_id != None:
            GObject.source_remove(self.fullscreen_hide_pointer_id)

        self.fullscreen_show_pointer()
        self.fullscreen_hide_pointer_id = GObject.timeout_add(3000, self.fullscreen_hide_pointer)


