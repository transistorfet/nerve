#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os.path
import traceback


class QuitException (Exception): pass


class ControllerMixIn (object):
    def on_connect(self):
        return

    def on_message(self, text, params=dict()):
        return

    def on_disconnect(self):
        return

    def handle_connection(self, request):
        self.conn = request.source
        self.on_connect()
        #while not self.conn.stopflag.is_set():
        #while not self.thread.stopflag.is_set():
        while True:
            try:
                msg = self.conn.read_message()
                if not msg:
                    break
                self.on_message(msg)

            except nerve.connect.QuitException:
                break

            except OSError as e:
                nerve.log("OSError: " + str(e))
                break

            except Exception as e:
                self.handle_connection_error(e, traceback.format_exc())

        self.on_disconnect()
        # TODO should this close maybe be on the server side?
        #self.conn.close()

    def handle_connection_error(self, error, tb):
        nerve.log(tb)


class Message (object):
    def __init__(self, text, mimetype='text/plain', **kwargs):
        for name in kwargs:
            setattr(self, kwargs[name])
        self.text = text
        self.mimetype = mimetype


class Connection (object):
    """
    # TODO this should maybe be implicit, in that the server end is expected to handle this part? (although it could be implemented for use by the server end)
    def connect(self, uri):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
    """

    def read_message(self):
        raise NotImplementedError

    def send_message(self, msg):    # (self, text, params=dict())
        raise NotImplementedError


