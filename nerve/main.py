#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import time
import json
import signal
import os.path
import traceback
import threading

import urllib.parse


rootnodes = [ ]


class RootNode (nerve.ObjectNode):
    def __init__(self, **config):
        super().__init__(**config)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_default_child('devices', { '__type__': 'objects/ObjectNode' })
        config_info.add_default_child('modules', { '__type__': 'modules/Module' })
        config_info.add_default_child('servers', { '__type__': 'objects/ObjectNode' })
        config_info.add_default_child('tasks', { '__type__': 'objects/ObjectNode' })
        return config_info

    def del_child(self, index):
        return False

    def init_system(self):
        try:
            nerve.asyncs.init()
            nerve.users.init()

            if not self.load_config('settings.json'):
                return False
            nerve.modules.run_module_inits()
            if not self.run_init('init.py'):
                return False
            return True
        except:
            nerve.log(traceback.format_exc(), logtype='error')
            return False

    def save_system(self):
        self.save_config('settings.saved.json')

    def load_config(self, filename):
        try:
            filename = nerve.files.find(filename)
        except OSError:
            nerve.log("error no 'settings.json' file found\n", logtype='error')
            return False

        try:
            with open(filename, 'r') as f:
                config = json.load(f)
                nerve.log("config loaded from " + filename, logtype='success')
        except:
            nerve.log("error loading config from " + filename + "\n\n" + traceback.format_exc(), logtype='error')
            return False

        self.set_config_data(config)
        return True

    def save_config(self, filename):
        filename = nerve.files.path(filename, create=True)
        config = self.get_config_data()
        with open(filename, 'w') as f:
            json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))

    def make_object_children(self, config):
        # TODO should defaults be set so that this conditional is no longer needed? (it will still need to extra the modules config)

        """
        # make sure to load the /modules config first
        if 'modules' in config:
            modules_config = config['modules']
            del config['modules']
        else:
            modules_config = { '__type__': 'objects/Module' }

        modules = nerve.ObjectNode.make_object(modules_config['__type__'], modules_config)
        self.set_child('modules', modules)
        """
        super().make_object_children(config)

    def run_init(self, filename):
        try:
            filename = nerve.files.find(filename)
        except OSError:
            return True

        nerve.log("running init script located at " + filename)
        try:
            with open(filename, 'r') as f:
                code = f.read()
            self.init = { 'nerve' : nerve }
            exec(code, self.init)
            nerve.log(filename + " has completed sucessfully", logtype='success')
            return True
        except:
            nerve.log("error running init from " + filename + "\n\n" + traceback.format_exc(), logtype='error')
            return False


class Main (RootNode):
    def __init__(self):
        super().__init__()
        self.exitcode = 0
        self.stopflag = threading.Event()

    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)

        if not self.init_system():
            self.shutdown()

        try:
            nerve.Thread.start_all()

            #print (dir(nerve))
            while not self.stopflag.wait(0.5):
                pass
            nerve.log("exiting main loop")

        except:
            nerve.log(traceback.format_exc(), logtype='error')

        self.shutdown()

    def signal_handler(self, signal, frame):
        self.stopflag.set()

    def restart(self):
        self.exitcode = 42
        self.stopflag.set()

    def shutdown(self):
        self.stopflag.set()
        nerve.log("shutting down all threads")
        nerve.Thread.stop_all()
        nerve.Thread.join_all()
        os.system('stty sane')
        sys.exit(self.exitcode)



def loop():
    global rootnodes

    main = Main()
    rootnodes.insert(0, main)
    main.start()

def new_root():
    global rootnodes

    root = RootNode()
    rootnodes.insert(0, root)
    root.init_system()
    return root

def root():
    global rootnodes
    if len(rootnodes) > 0:
        return rootnodes[0]
    return root()

def quit():
    global rootnodes
    rootnodes[0].stopflag.set()

def get_main():
    global rootnodes
    return rootnodes[0]

def save_config():
    global rootnodes
    return rootnodes[0].save_system()


def get_object(name):
    global rootnodes
    if name == "/":
        return rootnodes[0]
    return rootnodes[0].get_object(name.lstrip('/'))

def set_object(name, obj, **config):
    global rootnodes
    return rootnodes[0].set_object(name.lstrip('/'), obj, **config)

def del_object(name):
    global rootnodes
    if name == "/":
        return False
    return rootnodes[0].del_object(name.lstrip('/'))

def has_object(name):
    try:
        if nerve.get_object(name):
            return True
    except:
        pass
    return False




_scheme_handlers = { }

def register_scheme(scheme, handler):
    if type(scheme) != str:
        raise Exception("invalid uri scheme name: " + str(scheme))
    _scheme_handlers[scheme] = handler


def query(urlstring, *args, **kwargs):
    url = urllib.parse.urlparse(urlstring)

    scheme = url.scheme if url.scheme else 'local' if not url.netloc else 'http'
    if not scheme in _scheme_handlers:
        raise Exception("unsupported url scheme: " + scheme)
    return _scheme_handlers[scheme].query(url, *args, **kwargs)

def subscribe(topic, action, label=None, **eventmask):
    url = urllib.parse.urlparse(topic)

    scheme = url.scheme if url.scheme else 'local' if not url.netloc else 'ws'
    if not scheme in _scheme_handlers:
        raise Exception("unsupported url scheme: " + scheme)
    return _scheme_handlers[scheme].subscribe(url, action, label, **eventmask)

def unsubscribe(topic=None, action=None, label=None, **eventmask):
    url = urllib.parse.urlparse(topic)

    scheme = url.scheme if url.scheme else 'local' if not url.netloc else 'ws'
    if not scheme in _scheme_handlers:
        raise Exception("unsupported url scheme: " + scheme)
    return _scheme_handlers[scheme].unsubscribe(url, action, label, **eventmask)



@nerve.singleton
class LocalQueryHandler (nerve.QueryHandler):
    def query(self, _queryurl, *args, **kwargs):
        path = urllib.parse.unquote_plus(_queryurl.path)
        kwargs = nerve.Request.add_query_args(_queryurl, kwargs)
        args = nerve.Request.get_positional_args(args, kwargs)

        nerve.log("executing query: " + path + " " + repr(args) + " " + repr(kwargs), logtype='query')

        """
        obj = nerve.root().get_object(_queryurl.path.lstrip('/'))
        if callable(obj):
            result = obj(*args, **kwargs)
        else:
            result = obj
        """
        result = nerve.root().query(path.lstrip('/'), *args, **kwargs)

        self.print_result(result)
        return result

    def subscribe(self, url, action, label=None, **eventmask):
        topic = urllib.parse.unquote_plus(url.path).lstrip('/')
        nerve.events.subscribe(topic, action, label, **eventmask)

    def unsubscribe(self, url=None, action=None, label=None, **eventmask):
        topic = urllib.parse.unquote_plus(url.path).lstrip('/')
        nerve.events.unsubscribe(topic, action, label, **eventmask)


register_scheme('local', LocalQueryHandler)


