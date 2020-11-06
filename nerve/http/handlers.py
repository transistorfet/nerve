#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import cgi
import json
import requests
import websocket
import urllib.parse
import threading
import traceback


@nerve.singleton
class HTTPQueryHandler (nerve.QueryHandler):
    def query(self, _queryurl, *args, **kwargs):
        # TODO is this valid?  To have query options in the kwargs?  Might that cause problems for some things?  Should the key be deleted here if
        # present, so that it doesn't get encoded.
        #if 'query_method' in kwargs:
        #   method = kwargs['query_method']
        #   del kwargs['query_method']
        #else:
        #   method = 'POST'

        #method = kwargs['query_method'] if 'query_method' in kwargs else 'POST'

        args = nerve.Request.put_positional_args(args, kwargs)
        method = 'GET' if len(kwargs) <= 0 else 'POST'
        urlstring = urllib.parse.urlunparse((_queryurl.scheme, _queryurl.netloc, _queryurl.path, '', '', ''))

        nerve.log("executing query: " + method + " " + urlstring + " " + repr(args) + " " + repr(kwargs), logtype='query')

        r = requests.request(method, urlstring, json=None if method == 'GET' else kwargs)

        if r.status_code != 200:
            raise Exception("request to " + urlstring + " failed. " + str(r.status_code) + ": " + r.reason, r.text)

        (mimetype, pdict) = cgi.parse_header(r.headers['content-type'])
        if mimetype == 'application/json':
            result = r.json()
        elif mimetype == 'application/x-www-form-urlencoded':
            result = urllib.parse.parse_qs(r.text, keep_blank_values=True)
        else:
            result = r.text

        self.print_result(result)
        return result

nerve.register_scheme('http', HTTPQueryHandler)
nerve.register_scheme('https', HTTPQueryHandler)


class WaitEvent (object):
    def __init__(self, msg):
        self.ready = threading.Event()
        self.result = None
        self.msg = msg

    def __call__(self, timeout=10):
        if self.ready.wait(timeout) is True:
            return self.result
        return None

    def resolve(self, result):
        self.result = result
        self.ready.set()


class WebsocketConnection (websocket.WebSocketApp):
    def __init__(self, url):
        super().__init__(url, subprotocols=['application/json'], on_open=self.on_open, on_close=self.on_close, on_message=self.on_message, on_error=self.on_error)
        self.seq = 0
        self.url = url
        self.queue = [ ]
        self.pending = [ ]
        self.connected = False

        self.thread = nerve.Thread('WebsocketConnectionThread', target=self.run_forever)
        self.thread.daemon = True
        self.thread.start()

    def on_open(self, ws):
        self.connected = True
        for msg in self.queue:
            self.send(msg)
        self.queue = [ ]

    def on_close(self, ws):
        self.connected = False
        nerve.events.unsubscribe(label=str(id(self)))
        # TODO reconnect? maybe only if there are subscriptions

    def on_message(self, ws, msg):
        nerve.log(str(msg), logtype='debug')
        msg = json.loads(msg)
        if msg['type'] in [ 'reply', 'error' ]:
            self.resolve_pending(msg)
        elif msg['type'] == 'publish':
            msg['event']['topic'] = str(id(self)) + '/' + msg['event']['topic']
            #msg['event']['topic'] = self.url + '/' + msg['event']['topic']
            nerve.events.publish(**msg['event'])

    def resolve_pending(self, msg):
        delete = [ ]
        for event in self.pending:
            if event.msg['id'] == msg['id']:
                if msg['type'] == 'error':
                    pass
                    # TODO normally you'd throw an error within the waiting thread...
                event.resolve(msg['result'])
                delete.append(event)
        self.pending = [ event for event in self.pending if event not in delete ]

    def on_error(self, ws, msg):
        nerve.log(str(msg), logtype='error')

    def send_msg(self, msg):
        msg = json.dumps(msg)
        if not self.connected:
            self.queue.append(msg)
        else:
            self.send(msg)

    def send_query(self, query, **kwargs):
        self.seq += 1
        msg = { 'type': 'query', 'query': query, 'args': kwargs, 'id': self.seq }
        event = WaitEvent(msg)
        self.pending.append(event)
        self.send_msg(msg)
        return event()

    def subscribe(self, topic, action, label, **eventmask):
        self.send_msg({ 'type': 'subscribe', 'topic': topic, 'label': label })
        nerve.events.subscribe(str(id(self)) + '/' + topic, label=str(id(self)), action=action, **eventmask)
        #nerve.events.subscribe(self.url + '/' + topic, label=str(id(self)), action=action, **eventmask)

    def unsubscribe(self, topic=None, label=None):
        self.send_msg({ 'type': 'unsubscribe', 'topic': topic, 'label': label })
        nerve.events.unsubscribe(str(id(self)) + '/' + topic, label=str(id(self)), action=action, **eventmask)



@nerve.singleton
class WebsocketQueryHandler (nerve.QueryHandler):
    def __init__(self):
        self.connlist = { }

    def get_connection(self, url):
        if url not in self.connlist:
            # TODO you need to close the connection if it's sat idle for a certain time??
            self.connlist[url] = WebsocketConnection(url)
        return self.connlist[url]

    def query(self, _queryurl, *args, **kwargs):
        args = nerve.Request.put_positional_args(args, kwargs)
        #urlstring = urllib.parse.urlunparse((_queryurl.scheme, _queryurl.netloc, _queryurl.path, '', '', ''))
        urlstring = urllib.parse.urlunparse((_queryurl.scheme, _queryurl.netloc, 'socket', '', '', ''))

        nerve.log("executing query: " + urlstring + " " + _queryurl.path + " " + repr(args) + " " + repr(kwargs), logtype='query')

        ws = self.get_connection(urlstring)
        #self.seq += 1
        #ws.send(json.dumps({ 'type': 'query', 'query': urlstring, 'args': kwargs, 'id': self.seq }))
        result = ws.send_query(_queryurl.path, **kwargs)
        self.print_result(result)
        return result

    def subscribe(self, _queryurl, action, label=None, **eventmask):
        """
        def _on_event(event):
            nerve.log(event, logtype='warning')
            self.send_message(nerve.connect.Message('application/json', data={ 'type': 'publish', 'event': event }))
        print(msg, _on_event)
        nerve.events.subscribe('devices/' + msg.data['topic'], _on_event, label=str(id(self)))
        """
        urlstring = urllib.parse.urlunparse((_queryurl.scheme, _queryurl.netloc, 'socket', '', '', ''))
        ws = self.get_connection(urlstring)

        topic = urllib.parse.unquote_plus(_queryurl.path).lstrip('/')
        ws.subscribe(topic, action, label, **eventmask)

    def unsubscribe(self, _queryurl=None, action=None, label=None, **eventmask):
        urlstring = urllib.parse.urlunparse((_queryurl.scheme, _queryurl.netloc, 'socket', '', '', ''))
        ws = self.get_connection(urlstring)

        topic = urllib.parse.unquote_plus(_queryurl.path).lstrip('/')
        ws.unsubscribe(topic, action, label, **eventmask)


nerve.register_scheme('ws', WebsocketQueryHandler)

#def thing(event):
#    print("Hoy", event)
#nerve.subscribe('ws://kitty:8889/devices/deskclock/t0', thing)
#nerve.events.publish('devices/player/getsong', thing="Hey") 

