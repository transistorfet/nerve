#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import json
import os.path
import traceback


class QuitException (Exception): pass


protocols = {
    'text': 'text/plain',
    'json': 'application/json',
}

class ControllerMixIn (object):
    def on_connect(self):
        return

    def on_message(self, text, params=dict()):
        return

    def on_disconnect(self):
        return

    def handle_connection(self, request):
        self.conn = request.source
        self.protocol = request.get_header('Sec-Websocket-Protocol', 'text')
        mimetype = protocols[self.protocol] if self.protocol in protocols else 'text/plain'
        self.on_connect()
        #while not self.conn.stopflag.is_set():
        #while not self.thread.stopflag.is_set():
        while True:
            try:
                msg = self.conn.read_message(mimetype=mimetype)
                if not msg:
                    break
                self.on_message(msg)

            except nerve.connect.QuitException:
                break

            except OSError as e:
                nerve.log("OSError: " + str(e), logtype='error')
                break

            except Exception as e:
                self.handle_connection_error(e, traceback.format_exc())

        self.on_disconnect()
        # TODO should this close maybe be on the server side?
        #self.conn.close()

    def handle_connection_error(self, error, tb):
        nerve.log(tb, logtype='error')


class Message (object):
    def __init__(self, mimetype='text/plain', text=None, data=None, **kwargs):
        for name in kwargs:
            setattr(self, kwargs[name])
        self.mimetype = mimetype
        self.text = text
        self.data = data
        if mimetype == 'application/json':
            if text:
                self.data = json.loads(text)
            elif data:
                self.text = json.dumps(data)

    @staticmethod
    def to_json(data):
        return Message(mimetype='application/json', text=json.dumps(data))

    @staticmethod
    def from_json(text):
        return Message(mimetype='application/json', data=json.loads(text))


class Connection (object):
    """
    # TODO this should maybe be implicit, in that the server end is expected to handle this part? (although it could be implemented for use by the server end)
    def connect(self, uri):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
    """

    def read_message(self, mimetype='text/plain'):
        raise NotImplementedError

    def send_message(self, msg):    # (self, text, params=dict())
        raise NotImplementedError


