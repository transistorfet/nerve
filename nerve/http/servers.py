#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import socket
import os
import sys
import signal
import traceback

import socketserver
import http.server
import hashlib
import base64
import ssl

import cgi
import json
import mimetypes

import urllib.parse

import struct
import random


WS_OP_CONT = 0x0
WS_OP_TEXT = 0x1
WS_OP_BIN = 0x2

WS_OP_CONTROL = 0x8
WS_OP_CLOSE = 0x8
WS_OP_PING = 0x9
WS_OP_PONG = 0xa

WS_B1_FINBIT = 0x80
WS_B1_RSV = 0x70
WS_B1_OPCODE = 0x0f
WS_B2_MASKBIT = 0x80
WS_B2_LENGTH = 0x7f

class WebSocketError (Exception): pass


class HTTPRequestHandler (http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    server_version = "Nerve HTTP/0.3"

    def log_message(self, format, *args):
        nerve.log(self.address_string() + ' ' + format % args)

    def check_authorization(self):
        authdata = self.headers.get('Authorization')
        if not authdata:
            if not self.server.get_setting('allow_guest'):
                raise nerve.users.UserLoginError("you must provide a login name and password")
            return nerve.users.login('guest', '')

        (username, _, password) = base64.b64decode(bytes(authdata.split(' ')[-1], 'utf-8')).decode('utf-8').partition(':')

        if self.server.get_setting('use_usersdb'):
            return nerve.users.login(username, password)

        if self.server.username:
            if username != self.server.username or password != self.server.password:
                raise nerve.users.UserLoginError("invalid admin username and password")
            class contextmanager (object):
                def __enter__(self): pass
                def __exit__(self, type, value, traceback): pass
            return contextmanager()

        raise nerve.users.UserLoginError("you must provide a login name and password")

    def send_401(self, message):
        self.send_content(401, 'text/html', message, [ ('WWW-Authenticate', 'Basic realm="Secure Area"') ])

    def do_GET(self):
        try:
            with self.check_authorization():
                self.do_request('GET')
        except nerve.users.UserLoginError as e:
            self.send_401(str(e))

    def do_POST(self):
        try:
            with self.check_authorization():
                self.do_request('POST')
        except nerve.users.UserLoginError as e:
            self.send_401(str(e))

    def do_request(self, reqtype):
        """
        print(end="\n")
        for (key, value) in dict(self.headers).items():
            print(key + ":\t" + str(value))
        print(end="\n")
        """

        if not self.is_valid_path(self.path):
            self.send_404()

        if reqtype == 'POST':
            if 'content-type' in self.headers:
                (mimetype, pdict) = cgi.parse_header(self.headers['content-type'])
            else:
                mimetype = None         # empty post doesn't provide a content-type.

            if mimetype == None:
                postvars = { }
            elif mimetype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif mimetype == 'application/x-www-form-urlencoded':
                contents = self.rfile.read(int(self.headers['content-length'])).decode('utf-8')
                postvars = urllib.parse.parse_qs(contents, keep_blank_values=True)
            elif mimetype == 'application/json':
                contents = self.rfile.read(int(self.headers['content-length'])).decode('utf-8')
                postvars = json.loads(contents)
            else:
                raise Exception("unrecognized content-type in POST " + self.path + " (" + mimetype + ")")
        else:
            postvars = None

        request = nerve.Request(self, None, reqtype, self.path, postvars, headers=dict(self.headers))

        if self.headers['upgrade'] == 'websocket':
            self.handle_websocket(request)
            return

        controller = self.server.make_controller(request)
        controller.handle_request(request)

        mimetype = controller.get_mimetype()
        redirect = controller.get_redirect()
        error = controller.get_error()
        output = controller.get_output()

        if redirect:
            self.send_content(302, mimetype, output, [ ('Location', redirect) ])
        elif error:
            self.send_content(404 if type(error) is nerve.NotFoundError else 500, mimetype, output)
        else:
            self.send_content(200, mimetype, output)
        return

    def send_content(self, errcode, mimetype, content, headers=None):
        if isinstance(content, str):
            content = bytes(content, 'utf-8')
        self.send_response(errcode)
        self.send_header('Content-Type', mimetype)
        self.send_header('Content-Length', len(content))
        if headers:
            for (header, value) in headers:
                self.send_header(header, value)
        self.end_headers()
        self.wfile.write(content)

    def send_400(self):
        self.send_content(400, 'text/plain', '400 Bad Request')

    def send_404(self):
        self.send_content(404, 'text/plain', '404 Not Found')

    def handle_websocket(self, request):
        self.send_response(101, "Switching Protocols")
        self.send_header('Upgrade', 'websocket')
        self.send_header('Connection', 'Upgrade')
        key = hashlib.sha1(bytes(self.headers['Sec-WebSocket-Key'] + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11", 'utf-8')).digest()
        self.send_header('Sec-WebSocket-Accept', base64.b64encode(key).decode('utf-8'))
        self.end_headers()

        protocol = self.headers['Sec-WebSocket-Protocol']

        try:
            controller = self.server.make_controller(request)
            self.websocket_write_message('Welcome to the nerve webshell...\n')
            while True:
                self.websocket_write_message('>> ')
                data = self.websocket_read_message()
                if data == None:
                    break
                self.websocket_write_message(data + '\n')
                if data == 'quit':
                    break

                controller.handle_request(nerve.Request(self, None, 'QUERY', "/", { 'queries[]' : [ data ] }))
                mimetype = controller.get_mimetype()
                output = controller.get_output()

                if mimetype.startswith('text/'):
                    self.websocket_write_message(output, text=True)
                elif mimetype == 'application/json':
                    text = [ ]
                    results = json.loads(output.decode('utf-8'))
                    for item in results:
                        text.extend(item.replace(' ', '&nbsp;').split('\n'))
                    self.websocket_write_message('\n'.join(text), text=True)
                else:
                    self.websocket_write_message(output, text=False)

        except Exception as e:
            nerve.log(traceback.format_exc())
            self.websocket_send_close(500, repr(e))

        else:
            self.websocket_send_close(200, '')

        self.websocket_wait_for_close()
        return

    def websocket_read_message(self):
        data = b''
        msg_opcode = None
        while True:
            (opcode, payload, headbyte1, headbyte2) = self.websocket_read_frame()

            if headbyte1 & WS_B1_RSV:
                raise Exception("received an invalid frame where first byte is " + hex(headbyte1))
            if (headbyte2 & WS_B2_MASKBIT) == 0:
                raise Exception("received an invalid frame where second byte is " + hex(headbyte2))

            if opcode & WS_OP_CONTROL:
                if opcode == WS_OP_CLOSE:
                    return None
                elif opcode == WS_OP_PING:
                    nerve.log("websocket: recieved ping from " + ':'.join(self.client_address))
                    self.websocket_write_frame(WS_OP_PONG, payload)
                    continue
                elif opcode == WS_OP_PONG:
                    continue
                else:
                    raise Exception("received invalid opcode " + hex(opcode))

            else:
                if msg_opcode == None:
                    msg_opcode = opcode
                else:
                    if opcode != WS_OP_CONT:
                        raise Exception("expected CONT opcode, received " + hex(opcode))

                data += payload
                if headbyte1 & WS_B1_FINBIT:
                    break

        if msg_opcode == WS_OP_TEXT:
            return data.decode('utf-8')
        elif msg_opcode == WS_OP_BIN:
            return data
        raise Exception("expected non-control opcode, received " + hex(opcode))

    def websocket_read_frame(self):
        (headbyte1, headbyte2) = struct.unpack('!BB', self.websocket_read_bytes(2))
        opcode = headbyte1 & 0xf
        length = headbyte2 & WS_B2_LENGTH
        if length == 0x7e:
            length = struct.unpack("!H", self.websocket_read_bytes(2))
            if length == 0x7f:
                length = struct.unpack("!Q", self.websocket_read_bytes(8))
        maskkey = self.websocket_read_bytes(4) if headbyte2 & WS_B2_MASKBIT else None

        payload = self.websocket_read_bytes(length)
        if maskkey:
            payload = bytes(b ^ maskkey[i % 4] for (i, b) in enumerate(payload))

        #print("RECV: " + hex(headbyte1) + " " + hex(headbyte2) + " " + str(payload))

        return (opcode, payload, headbyte1, headbyte2)

    def websocket_read_bytes(self, num):
        return self.rfile.read(num)

    def websocket_write_message(self, data, text=True):
        if text is True:
            self.websocket_write_frame(WS_OP_TEXT, bytes(data, 'utf-8') if type(data) == str else data)
        else:
            self.websocket_write_frame(WS_OP_BIN, data)

    def websocket_send_close(self, statuscode, message):
        self.websocket_write_frame(WS_OP_CLOSE, struct.pack("!H", statuscode) + bytes(message, 'utf-8'))

    def websocket_wait_for_close(self):
        while True:
            (opcode, payload, headbyte1, headbyte2) = self.websocket_read_frame()
            if opcode == WS_OP_CLOSE:
                if payload:
                    nerve.log("websocket: received close message: " + str(struct.unpack("!H", payload[0:2])[0]) + " - " + payload[2:].decode('utf-8'))
                else:
                    nerve.log("websocket: received close message")
                return

    def websocket_write_frame(self, opcode, data):
        length = len(data)
        frame = b''
        frame += struct.pack("!B", WS_B1_FINBIT | opcode)
        if length < 0x7e:
            frame += struct.pack("!B", WS_B2_MASKBIT | length)
        elif length < 0xffff:
            frame += struct.pack("!BH", WS_B2_MASKBIT | 0x7e, length)
        else:
            frame += struct.pack("!BQ", WS_B2_MASKBIT | 0x7f, length)
        maskkey = struct.pack("!I", random.getrandbits(32))
        frame += maskkey
        frame += bytes(b ^ maskkey[i % 4] for (i, b) in enumerate(data))

        #print("SEND: " + ' '.join(hex(b) for b in frame))
        self.wfile.write(frame)
        #self.request.send(frame)

    @staticmethod
    def is_valid_path(path):
        if not path[0] == '/':
            return False
        for name in path.split('/'):
            if name == '.' or name == '..':
                return False
        return True


class HTTPServer (nerve.Server, socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

    def __init__(self, **config):
        nerve.Server.__init__(self, **config)

        self.username = self.get_setting("username")
        self.password = self.get_setting("password")

        http.server.HTTPServer.__init__(self, ('', self.get_setting('port')), HTTPRequestHandler)
        #if self.get_setting('ssl_enable'):
        #    self.socket = ssl.wrap_socket(self.socket, certfile=self.get_setting('ssl_cert'), server_side=True)

        sa = self.socket.getsockname()
        nerve.log('starting http(s) on port ' + str(sa[1]))

        self.thread = nerve.Task('HTTPServerTask', target=self.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('port', "Port", default=8888)
        config_info.add_setting('use_usersdb', "Use Users DB", default=True)
        config_info.add_setting('allow_guest', "Allow Guest", default=True)
        config_info.add_setting('username', "Admin Username", default='')
        config_info.add_setting('password', "Admin Password", default='')
        config_info.add_setting('ssl_enable', "SSL Enable", default=False)
        config_info.add_setting('ssl_cert', "SSL Certificate File", default='')
        return config_info


