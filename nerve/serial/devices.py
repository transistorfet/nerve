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
        super().__init__(**config)

        self.file = self.get_setting('file')
        self.baud = self.get_setting('baud')

        if not self.get_setting('enabled'):
            return

        self.thread = nerve.Task('SerialTask', self.run)

        if sys.platform == 'win32':
            self.thread.daemon = True
            self.readline_func = self.readline_win32
        else:
            self.readline_func = self.readline_posix

        self.thread.start()

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('enabled', "Enable on Startup", default=True)
        config_info.add_setting('file', "Device File", default='/dev/ttyS0')
        config_info.add_setting('baud', "Baud Rate", default=19200)
        return config_info

    def send(self, data):
        #nerve.log("SEND -> " + str(self.file) + ": " + data)
        self.serial.write(bytes(data + '\n', 'utf-8'))

    def on_connect(self):
        pass

    def on_receive(self, line):
        pass

    def on_idle(self):
        pass

    def on_disconnect(self):
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
                filename = self.get_setting('file')
                baud = self.get_setting('baud')
                self.serial = serial.Serial(filename, baud)
                self.on_connect()

            except serial.serialutil.SerialException as exc:
                nerve.log("serial error: " + str(exc), logtype='error')
                self.thread.stopflag.wait(30)

            else:
                while not self.thread.stopflag.is_set():
                    try:
                        self.on_idle()
                        line = self.readline_func()
                        if line:
                            line = line.decode('utf-8').strip()
                            self.on_receive(line)

                    except serial.serialutil.SerialException as exc:
                        nerve.log("serial error: " + repr(exc), logtype='error')
                        break

                    except:
                        nerve.log(traceback.format_exc(), logtype='error')
                self.on_disconnect()


class NerveSerialQuery (object):
    def __init__(self, dev, ref):
        self.ready = threading.Event()
        self.dev = dev
        self.ref = ref
        self.result = None

    def __call__(self, *args, **kwargs):
        query_string = self.ref
        if len(args) > 0:
            query_string += ' ' + ' '.join(args)

        self.ready.clear()
        self.dev.enqueue_and_send(self, query_string)
        if self.ready.wait(2) is True:
            return self.result
        return None


class NerveSerialDevice (SerialDevice):
    def __init__(self, **config):
        super().__init__(**config)
        self.lock = threading.Lock()
        self.waiting = [ ]

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('query', "Emit Query", default='/events/serial')
        config_info.add_setting('publish', "Publish Events?", default=False)
        config_info.add_default_child('event_recv', { '__type__': 'objects/ObjectNode' })
        return config_info

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

    def on_receive(self, line):
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

        if self.get_setting('publish'):
            nerve.events.publish(type='change', src=self.get_pathname() + '/' + ref, value=args)

        # TODO this isn't really used anymore (actually it is still the main interface to irremote, but should be replace with events when that gets working)
        if not args:
            return
        notify_ref = self.get_setting('query').rstrip('/') + '/' + ref + '/*'
        nerve.query(notify_ref, args)

        #self.query('event_recv/*', args)

        #print("Received unmatched serial return: " + ref + " " + str(args))
        #nerve.query("/events/ir/irrecv/" + args)

        #nerve.query("/events/ir/irrecv/*")
        # this would then call all the events in the irrecv 'directory'
        # or would this just be a query...


