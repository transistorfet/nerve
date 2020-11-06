#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.http
import nerve.connect

import traceback


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
        if msg.mimetype != 'application/json':
            nerve.log("invalid message type: " + str(msg.mimetype) + " " + str(msg.text))
            return

        nerve.log(msg.mimetype + " " + str(msg.data), logtype='warning')
        if msg.data['type'] == 'query':
            try:
                seq = msg.data['id'] if 'id' in msg.data else 0
                args = msg.data['args'] if 'args' in msg.data and msg.data['args'] else {}
                result = nerve.query(msg.data['query'], **args)
                self.send_message(nerve.connect.Message('application/json', data={ 'type': 'reply', 'id': seq, 'query': msg.data['query'], 'result': result }))
            except Exception as e:
                t = traceback.format_exc()
                nerve.log(t, logtype='error')
                self.send_message(nerve.connect.Message('application/json', data={ 'type': 'error', 'id': seq, 'query': msg.data['query'], 'stack': t, 'error': type(e).__name__ + ": " + str(e) }))

        elif msg.data['type'] == 'subscribe':
            def _on_event(event):
                nerve.log(event, logtype='warning')
                self.send_message(nerve.connect.Message('application/json', data={ 'type': 'publish', 'event': event }))
            print(msg, _on_event)
            nerve.events.subscribe(msg.data['topic'], _on_event, label=str(id(self)))

        elif msg.data['type'] == 'unsubscribe':
            nerve.events.unsubscribe(msg.data['topic'], label=str(id(self)))

    def send_message(self, msg):
        if hasattr(self, 'conn'):
            #if self.protocol.split(';')[0] == 'application/json' and msg.mimetype != 'application/json':
            #    msg = nerve.connect.Message(mimetype='application/json', data={ type: 'log', text: msg.text })
            self.conn.send_message(msg)

    def handle_connection_error(self, error, traceback):
        nerve.log(traceback, logtype='error')
        #self.send_message(nerve.connect.Message(text=traceback))
        self.send_message(nerve.connect.Message(mimetype='application/json', data={ 'type': 'error', 'text': traceback }))

