#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.connect

import os
import sys
import socket
import string
import traceback


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
        config_info.set_default('controllers', default={
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

                except OSError as e:
                    nerve.log("OSError: " + str(e))
                    break

                except:
                    nerve.log(traceback.format_exc())

            nerve.log("closing socket and retrying in 5 seconds")
            self.socket.close()
            time.sleep(5)


class TCPConnection (nerve.connect.Connection):
    def __init__(self, server, socket, addr):
        super().__init__()
        self.server = server
        self.socket = socket
        (self.hostname, self.port) = addr
        self.rfile = self.socket.makefile(mode='r', encoding='utf-8', newline='\n')

        self.thread = nerve.Task('TCPConnectionTask:' + self.hostname + ':' + str(self.port), self.run)
        self.thread.daemon = True
        self.thread.start()

    def read_message(self):
        line = self.rfile.readline()
        if not line:
            return None
        line = line.strip('\n')
        nerve.log("RECV <- " + str(self.hostname) + ":" + str(self.port) + ": " + line)
        return nerve.connect.Message(text=line)

    def send_message(self, msg):
        #nerve.log("SEND -> " + str(self.hostname) + ":" + str(self.port) + ": " + data)
        #self.socket.send(bytes(data + '\n', 'utf-8'))
        self.socket.send(bytes(msg.text + '\n', 'utf-8'))

    def close(self):
        nerve.log("closing connection to " + str(self.hostname) + ":" + str(self.port))
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def run(self):
        request = nerve.Request(self, None, 'CONNECT', '/', dict(), headers=dict(accept='text/plain'))
        controller = self.server.make_controller(request)
        controller.handle_request(request)
        self.close()
        self.thread.delete()
        return

        """
        while not self.thread.stopflag.is_set():
            try:
                data = self.rfile.readline()
                data = data.strip('\n')
                if data:
                    nerve.log("RECV <- " + str(self.hostname) + ":" + str(self.port) + ": " + data)

                    if data == 'quit':
                        self.thread.stopflag.set()
                    else:
                        request = nerve.Request(self, None, 'QUERY', "/", { 'requests[]' : [ data ] })
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
        """


