#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import time
import signal
import os.path
import argparse
import traceback
import threading

import cgi
import json
import requests
import urllib.parse

mainloops = [ ]


class Main (nerve.ObjectNode):
    def __init__(self):
        super().__init__()
        self.exitcode = 0
        self.stopflag = threading.Event()

        parser = argparse.ArgumentParser(prog='nerve', formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Nerve Control Server')
        parser.add_argument('-c', '--configdir', action='store', help='Use specified directory for configuration', default='~/.nerve/')
        self.args = parser.parse_args()

        self.configdir = self.args.configdir.strip('/')
        if not os.path.exists(self.configdir):
            os.mkdir(self.configdir)
            self.save_config(os.path.join(self.configdir, 'settings.json'))

        sys.path.insert(0, ( sys.path[0] + '/' if self.configdir[0] != '/' else '' ) + self.configdir)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        """
        # TODO this is now wrong... these items are children of the parent object, not settings
        child_info.add_setting('modules', "Modules", default=nerve.Module())
        child_info.add_setting('devices', "Devices", default=nerve.ObjectNode())
        child_info.add_setting('events', "Events", default=nerve.ObjectNode())
        child_info.add_setting('servers', "Servers", default=nerve.ObjectNode())
        """
        return config_info

    def del_child(self, index):
        return False

    def getdir(self):
        return self.configdir

    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        self.eventpool = nerve.events.EventThreadPool()
        self.eventpool.start()

        nerve.users.init()

        try:
            if not self.load_config(os.path.join(self.configdir, 'settings.json')):
                self.shutdown()
            if not self.run_init():
                self.shutdown()

            nerve.Task.start_all()

            #print (dir(nerve))
            while not self.stopflag.wait(0.5):
                pass
            nerve.log("exiting main loop")
        except:
            nerve.log(traceback.format_exc())

        self.shutdown()

    def signal_handler(self, signal, frame):
        self.stopflag.set()

    def restart(self):
        self.exitcode = 42
        self.stopflag.set()

    def shutdown(self):
        self.stopflag.set()
        nerve.log("shutting down all threads")
        nerve.Task.stop_all()
        nerve.Task.join_all()
        os.system('stty sane')
        sys.exit(self.exitcode)

    def run_init(self):
        filename = os.path.join(self.configdir, 'init.py')
        if not os.path.exists(filename):
            return True

        nerve.log("running init script located at " + filename)
        try:
            with open(filename, 'r') as f:
                code = f.read()
            self.init = { 'nerve' : nerve }
            exec(code, self.init)
            nerve.log(filename + " has completed sucessfully")
            return True
        except:
            nerve.log("error running init from " + filename + "\n\n" + traceback.format_exc())
            return False

    def load_config(self, filename):
        #config = self.get_config_info().get_defaults()

        if not os.path.exists(filename):
            nerve.log("error config not found in " + filename + "\n")
            return False

        try:
            with open(filename, 'r') as f:
                config = json.load(f)
                nerve.log("config loaded from " + filename)
        except:
            nerve.log("error loading config from " + filename + "\n\n" + traceback.format_exc())
            return False

        self.set_config_data(config)
        return True

    def make_object_children(self, config):
        # TODO should defaults be set so that this conditional is no longer needed? (it will still need to extra the modules config)

        # make sure to load the /modules config first
        if 'modules' in config:
            modules_config = config['modules']
            del config['modules']
        else:
            modules_config = { '__type__': 'objects/Module' }

        modules = nerve.Module.make_object(modules_config['__type__'], modules_config)
        self.set_child('modules', modules)
        super().make_object_children(config)

    def save_config(self, filename):
        config = self.get_config_data()
        with open(filename, 'w') as f:
            json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))

    def load_file(self, filename):
        filename = os.path.join(self.configdir, filename)
        (path, _, _) = filename.rpartition('/')
        if not os.path.isdir(path):
            os.makedirs(path)
        if not os.path.isfile(filename):
            with open(filename, 'w'):
                pass
        with open(filename, 'r') as f:
            contents = f.read()
        return contents

    def save_file(self, filename, contents):
        filename = os.path.join(self.configdir, filename)
        (path, _, _) = filename.rpartition('/')
        if not os.path.isdir(path):
            os.makedirs(path)
        with open(filename, 'w') as f:
            f.write(contents)


def loop():
    global mainloops

    main = Main()
    mainloops.insert(0, main)
    main.start()

def quit():
    global mainloops
    mainloops[0].stopflag.set()

def get_main():
    global mainloops
    return mainloops[0]

def configdir():
    global mainloops
    return mainloops[0].getdir()

def save_config():
    global mainloops
    return mainloops[0].save_config(os.path.join(nerve.configdir(), 'settings.saved.json'))


def get_object(name):
    global mainloops
    if name == "/":
        return mainloops[0]
    return mainloops[0].get_object(name.lstrip('/'))

def set_object(name, obj, **config):
    global mainloops
    return mainloops[0].set_object(name.lstrip('/'), obj, **config)

def del_object(name):
    global mainloops
    if name == "/":
        return False
    return mainloops[0].del_object(name.lstrip('/'))

def has_object(name):
    try:
        if nerve.get_object(name):
            return True
    except:
        pass
    return False


def query(urlstring, *args, **kwargs):
    global mainloops

    nerve.log("executing query: " + urlstring + " " + repr(args) + " " + repr(kwargs))
    url = urllib.parse.urlparse(urlstring)

    if url.netloc:
        if url.scheme == 'http':
            # TODO we ignore args and kwargs when querying a http server.  We could automatically make a query string of kwargs, and possible
            #      still ignore args, or we could use a POST request instead, and send the json of the arguments (possible JSON-RPC style)

            if len(kwargs) <= 0:
                nerve.log("remote query: GET " + urlstring)
                r = requests.get(urlstring)
            else:
                # TODO should there be an option to encode the args as json?
                nerve.log("remote query: POST " + urlstring)
                r = requests.post(urlstring, data=kwargs)

            if r.status_code != 200:
                raise Exception("request to " + urlstring + " failed. " + str(r.status_code) + ": " + r.reason, r.text)

            (mimetype, pdict) = cgi.parse_header(r.headers['content-type'])
            if mimetype == 'application/json':
                return json.loads(r.text)
            elif mimetype == 'application/x-www-form-urlencoded':
                return urllib.parse.parse_qs(r.text, keep_blank_values=True)
            else:
                return r.text

        else:
            raise Exception("unsupported url scheme: " + url.scheme)

    else:
        (url, kwargs) = nerve.Request.parse_query(urlstring, kwargs)

        obj = mainloops[0].get_object(url.path.lstrip('/'))
        if callable(obj):
            result = obj(*args, **kwargs)
        else:
            result = obj

        rstr = str(result)
        nerve.log("result: " + ( rstr[:75] + '...' if len(rstr) > 75 else rstr ))
        return result

def notify(querystring, *args, **kwargs):
    global mainloops
    return mainloops[0].notify(name.lstrip('/'), obj, **config)


def load_file(filename):
    global mainloops
    return mainloops[0].load_file(filename)

def save_file(filename, contents):
    global mainloops
    return mainloops[0].save_file(filename, contents)


