#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import socket
import thread
import sys
import os
import time
import traceback
import string


class UDPServer (nerve.Server):
    def __init__(self, **config):
        nerve.Server.__init__(self, **config)

        self.port = config['port'] if 'port' in config else 5959

        self.thread = nerve.Task('UDPServerTask', target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.port))

    def close(self):
        addr, port = self.socket.getsockname()
        nerve.log("closing socket %s:%s" % (addr, port))
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def receive(self):
        data, addr = self.socket.recvfrom(8192)
        if not data:
            raise socket.error("UDP socket closed on port " + self.port)
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
                    if (data):
                        nerve.log("RECV <- " + str(host) + ":" + str(port) + ": " + data)
                        result = nerve.query_string(data)
                        self.send(repr(result), addr)

                        #args = data.split()
                        #request = nerve.Request(self, 'QUERY', args[0], { })
                        #controller = self.find_controller(request)
                        #controller.handle_request(request)

                except socket.error, e:
                    nerve.log("Socket Error: " + str(e))
                    break

                except:
                    nerve.log(traceback.format_exc())

            nerve.log("closing socket and retrying in 5 seconds")
            self.close()
            time.sleep(5)

 
