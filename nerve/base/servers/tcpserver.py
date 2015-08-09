#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import socket
import string
import traceback


class TCPConnection (nerve.Server):
    def __init__(self, server, socket, addr):
        super().__init__()
        self.server = server
        self.socket = socket
        (self.host, self.port) = addr

        self.buffer = ""

        self.thread = nerve.Task('TCPConnectionTask:' + self.host + ':' + str(self.port), self.run)
        self.thread.daemon = True
        self.thread.start()

    def readline(self):
        while 1:
            if self.buffer:
                i = self.buffer.find('\n')
                if i >= 0:
                    line = self.buffer[:i].strip('\n\r')
                    self.buffer = self.buffer[i+1:]
                    return line
            data = self.socket.recv(4096)
            if not data:
                raise socket.error("TCP socket closed by remote end. (" + str(self.host) + ":" + str(self.port) + ")")
            self.buffer = self.buffer + data.decode('utf-8')

    def send(self, data):
        #nerve.log("SEND -> " + str(self.host) + ":" + str(self.port) + ": " + data)
        self.socket.send(data + b'\n')

    def close(self):
        nerve.log("closing connection to " + str(self.host) + ":" + str(self.port))
        self.socket.close()

    def run(self):
        while not self.thread.stopflag.is_set():
            try:
                data = self.readline()
                data = data.strip('\n')
                if data:
                    nerve.log("RECV <- " + str(self.host) + ":" + str(self.port) + ": " + data)

                    if data == 'quit':
                        self.thread.stopflag.set()
                    else:
                        request = nerve.Request(self, None, 'QUERY', "/", { 'queries[]' : [ data ] })
                        controller = self.server.make_controller(request)
                        controller.handle_request(request)
                        self.send(controller.get_output())

            except socket.error as e:
                nerve.log("Socket Error: " + str(e))
                break

            except:
                nerve.log(traceback.format_exc())
        self.close()
        self.thread.delete()


class TCPServer (nerve.Server):
    def __init__(self, **config):
        super().__init__(**config)

        port = self.get_setting('port')
        self.thread = nerve.Task('TCPServerTask:' + str(port), self.run)
        self.thread.daemon = True
        self.thread.start()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('port', "Port", default=12345)
        config_info.add_setting('controllers', "Controllers", default={
            '__default__' : {
                '__type__' : 'base/ShellController'
            }
        })
        return config_info

    def listen(self):
        port = self.get_setting('port')
        nerve.log("starting tcp server on port " + str(port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', port))
        self.socket.listen(5)

    def close(self):
        self.running = 0;
        self.socket.close()

    def run(self):
        while not self.thread.stopflag.is_set():
            self.listen()
            while not self.thread.stopflag.is_set():
                try:
                    sock, addr = self.socket.accept()
                    conn = TCPConnection(self, sock, addr)

                except socket.error as e:
                    nerve.log("Socket Error: " + str(e))
                    break

                except:
                    nerve.log(traceback.format_exc())

            nerve.log("closing socket and retrying in 5 seconds")
            self.socket.close()
            time.sleep(5)


