#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import sys
import time
import serial
import select
import traceback
import threading

class SerialDevice (nerve.Device):
    def __init__(self, **config):
        nerve.Device.__init__(self, **config)

        self.file = config['file']
        self.baud = config['baud']

        self.thread = nerve.Task('SerialTask', self.run)

        if sys.platform == 'win32':
            self.thread.daemon = True
            self.readline_func = self.readline_win32
        else:
            self.readline_func = self.readline_posix

        self.thread.start()

    @staticmethod
    def get_config_info():
        config_info = nerve.Device.get_config_info()
        config_info.add_setting('file', "Device File", default='/dev/ttyS0')
        config_info.add_setting('baud', "Baud Rate", default=19200)
        return config_info

    def send(self, data):
        #nerve.log("SEND -> " + str(self.file) + ": " + data)
        self.serial.write(bytes(data + '\n', 'utf-8'))

    def do_receive(self, line):
        pass

    def do_idle(self):
        pass

    def readline_posix(self):
        (rl, wl, el) = select.select([ self.serial ], [ ], [ ], 1)
        if rl and self.serial in rl:
            return self.serial.readline()
        else:
            return None

    def readline_win32(self):
        return self.serial.readline()

    def run(self):
        while not self.thread.stopflag.is_set():
            try:
                self.serial = serial.Serial(self.file, self.baud)

            except serial.serialutil.SerialException as exc:
                nerve.log("serial error: " + str(exc))
                self.thread.stopflag.wait(30)

            else:
                while not self.thread.stopflag.is_set():
                    try:
                        self.do_idle()
                        line = self.readline_func()
                        if line:
                            line = line.decode('utf-8').strip()
                            self.do_receive(line)

                    except serial.serialutil.SerialException as exc:
                        nerve.log("serial error: " + repr(exc))
                        break

                    except:
                        nerve.log(traceback.format_exc())


class NerveSerialQuery (object):
    def __init__(self, dev, ref):
        self.ready = threading.Event()
        self.dev = dev
        self.ref = ref
        self.result = None

    def __call__(self, *args, **kwargs):
        args = list(args)
        query_string = self.ref
        for arg in [ 'a', 'b', 'c', 'd', 'e', 'f' ]:
            if arg in kwargs:
                args.append(kwargs[arg])
            else:
                break
        if len(args) > 0:
            query_string += ' ' + ' '.join(args)

        self.ready.clear()
        self.dev.enqueue_and_send(self, query_string)
        if self.ready.wait(2) is True:
            return self.result
        return None


class NerveSerialDevice (SerialDevice):
    def __init__(self, **config):
        SerialDevice.__init__(self, **config)
        self.lock = threading.Lock()
        self.waiting = [ ]

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            pass
        return NerveSerialQuery(self, name)

    def enqueue_and_send(self, query, query_string):
        nerve.log("SEND -> " + query_string)
        with self.lock:
            self.waiting.append(query)
        self.send(query_string)

    def do_receive(self, line):
        nerve.log("RECV <- " + self.file + ": " + line)
        (ref, _, args) = line.partition(" ")
        if not ref:
            return
        with self.lock:
            for (i, query) in enumerate(self.waiting):
                if query.ref == ref:
                    self.waiting.pop(i)
                    query.result = args
                    query.ready.set()
                    return

        if not args:
            return
        print("Received unmatched serial return: " + ref + " " + str(args))
        nerve.query("/events/ir/irrecv/" + args)

        #nerve.notify("/events/ir/irrecv")
        # this would then call all the events in the irrecv 'directory'
        # or would this just be a query...


