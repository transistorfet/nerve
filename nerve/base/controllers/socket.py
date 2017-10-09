#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http
import nerve.connect


class SocketController (nerve.http.Controller, nerve.connect.ControllerMixIn):
    def __init__(self, **config):
        super().__init__(**config)

    @nerve.public
    def index(self, request):
        if request.reqtype == 'CONNECT':
            self.handle_connection(request)
        else:
            data = { }
            #data['hostname'] = self.server.hostname
            #data['linebuffer'] = list(self.client.linebuffer)
            #self.load_template_view('nerve/connect/views/client.blk.pyhtml', data, request)

    def on_disconnect(self):
        nerve.events.unsubscribe(label=str(id(self)))

    def on_message(self, msg):
        if msg.mimetype == 'application/json':
            nerve.log(msg.mimetype + " " + str(msg.data), logtype='warning')
            if msg.data['type'] == 'query':
                args = msg.data['args'] if 'args' in msg.data else {}
                query = ('' if msg.data['query'].startswith('/') else '/devices/') + msg.data['query']
                result = nerve.query(query, **args)
                self.send_message(nerve.connect.Message('application/json', data={ 'type': 'reply', 'query': msg.data['query'], 'result': result, 'id': msg.data['id'] if id in msg.data else 0 }))
            elif msg.data['type'] == 'subscribe':
                def _on_event(event):
                    nerve.log(event, logtype='warning')
                    self.send_message(nerve.connect.Message('application/json', data={ 'type': 'publish', 'event': event }))
                print(msg, _on_event)
                nerve.events.subscribe('devices/' + msg.data['topic'], _on_event, label=str(id(self)))

    def send_message(self, msg):
        if hasattr(self, 'conn'):
            self.conn.send_message(msg)

    def handle_connection_error(self, error, traceback):
        nerve.log(traceback, logtype='error')
        self.send_message(nerve.connect.Message(text=traceback))

