#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import socket
import sys
import os
import time
import traceback
import string


class UDPServer (nerve.Server):
    def __init__(self, **config):
        super().__init__(**config)

        port = self.get_setting('port')
        self.thread = nerve.Task('UDPServerTask:' + str(port), target=self.run)
        self.thread.daemon = True
        self.thread.start()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('port', "Port", default=5959)
        config_info.set_default('controllers', default={
            '__default__' : {
                '__type__' : 'base/QueryController'
            }
        })
        return config_info

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.get_setting('port')))

    def close(self):
        addr, port = self.socket.getsockname()
        nerve.log("closing socket %s:%s" % (addr, port))
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def receive(self):
        data, addr = self.socket.recvfrom(8192)
        if not data:
            raise socket.error("UDP socket closed on port " + self.get_setting('port'))
        return data, addr

    def send(self, data, addr):
        (host, port) = addr
        nerve.log("SEND -> " + str(host) + ":" + str(port) + ": " + data)
        self.socket.sendto(data + '\n', addr)

    def run(self):
        nerve.log("Starting UDP Server")
        while True:
            self.open()

            while True:
                try:
                    data, addr = self.receive()
                    data = data.strip('\n')
                    (host, port) = addr
                    if data:
                        nerve.log("RECV <- " + str(host) + ":" + str(port) + ": " + data)
                        request = nerve.Request(self, None, 'QUERY', "/", { 'requests[]' : [ data ] })
                        controller = self.make_controller(request)
                        controller.handle_request(request)
                        self.send(controller.get_output() + '\n', addr)

                except socket.error as e:
                    nerve.log("Socket Error: " + str(e), logtype='error')
                    break

                except:
                    nerve.log(traceback.format_exc(), logtype='error')

            nerve.log("closing socket and retrying in 5 seconds")
            self.close()
            time.sleep(5)

 
