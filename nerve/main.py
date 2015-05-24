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

import json
import requests
import urllib.parse

mainloops = [ ]
#stdout = sys.stdout


class Main (nerve.ObjectNode):
    def __init__(self):
        super().__init__()
        self.stopflag = threading.Event()

        parser = argparse.ArgumentParser(prog='nerve', formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Nerve Control Server')
        parser.add_argument('-c', '--configdir', action='store', help='Use specified directory for configuration', default='~/.nerve/')
        self.args = parser.parse_args()

        self.configdir = self.args.configdir.strip('/')
        sys.path.insert(0, ( sys.path[0] + '/' if self.configdir[0] != '/' else '' ) + self.configdir)

    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        config_info.add_setting('modules', "Modules", default=nerve.ModulesDirectory())
        config_info.add_setting('devices', "Devices", default=nerve.ObjectNode())
        config_info.add_setting('events', "Events", default=nerve.ObjectNode())
        config_info.add_setting('servers', "Servers", default=nerve.ObjectNode())
        return config_info

    def del_child(self, index):
        return False

    def getdir(self):
        return self.configdir

    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        try:
            if not self.load_config(os.path.join(self.configdir, 'settings.json')):
                self.shutdown()
            if not self.run_init():
                self.shutdown()

            #print (dir(nerve))
            while not self.stopflag.wait(0.5):
                pass
            nerve.log("exiting main loop")
        except:
            nerve.log(traceback.format_exc())

        self.shutdown()

    def signal_handler(self, signal, frame):
        self.stopflag.set()

    def shutdown(self):
        nerve.log("shutting down all threads")
        nerve.Task.stop_all()
        nerve.Task.join_all()
        os.system('stty sane')
        sys.exit(0)

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
        config = self.get_config_info().get_defaults()

        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                    nerve.log("config loaded from " + filename)
            except:
                nerve.log("error loading config from " + filename + "\n\n" + traceback.format_exc())
                return False
        #nerve.ModulesDirectory.preload_modules(config['__children__']['modules']['autoload'])
        self.set_config_data(config)
        return True

    def save_config(self, filename):
        config = self.get_config_data()
        with open(filename, 'w') as f:
            json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))

    def read_config_file(self, filename):
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

    def write_config_file(self, filename, contents):
        filename = os.path.join(self.configdir, filename)
        (path, _, _) = filename.rpartition('/')
        if not os.path.isdir(path):
            os.makedirs(path)
        with open(filename, 'w') as f:
            f.write(contents)


"""
def log(text):
    global stdout
    stdout.write(time.strftime("%Y-%m-%d %H:%M") + " " + text + "\n")
"""

def loop():
    global mainloops

    main = Main()
    mainloops.insert(0, main)
    main.start()

def quit():
    global mainloops
    mainloops[0].stopflag.set()

def main():
    global mainloops
    return mainloops[0]

def get_config_info():
    global mainloops
    return mainloops[0].get_config_info()

def get_config_data():
    global mainloops
    return mainloops[0].get_config_data()

def configdir():
    global mainloops
    return mainloops[0].getdir()

def save_config():
    global mainloops
    return mainloops[0].save_config(os.path.join(nerve.configdir(), 'settings.saved.json'))

def set_object(name, obj, **config):
    global mainloops
    return mainloops[0].set_object(name.lstrip('/'), obj, **config)

def get_object(name):
    global mainloops
    if name == "/":
        return mainloops[0]
    return mainloops[0].get_object(name.lstrip('/'))

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

    nerve.log("executing query: " + urlstring + " " + ' '.join([ repr(val) for val in args ]) + " " + repr(kwargs))
    url = urllib.parse.urlparse(urlstring)

    if url.netloc:
        if url.scheme == 'http':
            nerve.log("remote query to " + urlstring)
            r = requests.get(urlstring)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                return "request to " + urlstring + " failed. " + str(r.status_code) + " returned"
        else:
            raise Exception("unsupported url scheme: " + url.scheme)

    else:
        (url, kwargs) = nerve.Request.parse_query(urlstring, kwargs)

        obj = mainloops[0].get_object(url.path.lstrip('/'))
        if callable(obj):
            return obj(*args, **kwargs)
        else:
            return obj

def query_string(text):
    # TODO parse quotes
    args = text.split()
    ref = args.pop(0)
    return query(ref, *args)

def notify(querystring, *args, **kwargs):
    if not querystring.endswith('/*'):
        raise Exception("Invalid notify query: " + querystring)
    parent = nerve.get_object(querystring[:-2])
    for objname in parent.keys_children():
        obj = parent.get_child(objname)
        if callable(obj):
            obj(*args, **kwargs)

def read_config_file(filename):
    global mainloops
    return mainloops[0].read_config_file(filename)

def write_config_file(filename, contents):
    global mainloops
    return mainloops[0].write_config_file(filename, contents)

