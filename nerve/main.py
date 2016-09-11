#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import time
import signal
import os.path
import traceback
import threading

import cgi
import json
import requests
import urllib.parse


rootnodes = [ ]


class RootNode (nerve.ObjectNode):
    def __init__(self, **config):
        super().__init__(**config)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_default_child('devices', { '__type__': 'objects/ObjectNode' })
        config_info.add_default_child('events', { '__type__': 'objects/ObjectNode' })
        config_info.add_default_child('modules', { '__type__': 'objects/Module' })
        config_info.add_default_child('servers', { '__type__': 'objects/ObjectNode' })
        return config_info

    def del_child(self, index):
        return False

    def init_system(self):
        try:
            nerve.asyncs.init()
            nerve.users.init()

            if not self.load_config('settings.json'):
                return False
            if not self.run_init('init.py'):
                return False
            return True
        except:
            nerve.log(traceback.format_exc(), logtype='error')
            return False

    def save_system(self):
        self.save_config('settings.saved.json')

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

        modules = nerve.Module.make_object(modules_config['__type__'], modules_config)
        self.set_child('modules', modules)
        """
        super().make_object_children(config)


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
            nerve.Task.start_all()

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
        nerve.Task.stop_all()
        nerve.Task.join_all()
        os.system('stty sane')
        sys.exit(self.exitcode)



def loop():
    global rootnodes

    main = Main()
    rootnodes.insert(0, main)
    main.start()

def root():
    global rootnodes

    root = RootNode()
    rootnodes.insert(0, root)
    root.init_system()

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

""""
def query(urlstring, *args, **kwargs):
    global rootnodes

    url = urllib.parse.urlparse(urlstring)

    if url.netloc:
        if url.scheme == 'http':
            # TODO we ignore args and kwargs when querying a http server.  We could automatically make a query string of kwargs, and possible
            #      still ignore args, or we could use a POST request instead, and send the json of the arguments (possible JSON-RPC style)

            nerve.log("executing query: " + url.path + " " + repr(args) + " " + repr(kwargs), logtype='query')

            # TODO is this valid?  To have query options in the kwargs?  Might that cause problems for some things?  Should the key be deleted here if
            # present, so that it doesn't get encoded.
            #if 'query_method' in kwargs:
            #   method = kwargs['query_method']
            #   del kwargs['query_method']
            #else:
            #   method = 'POST'

            #method = kwargs['query_method'] if 'query_method' in kwargs else 'POST'

            for i in range(len(args)):
                #if '$'+str(i) in kwargs:
                #   raise ValueError("positional argument " + '$'+str(i) + " already exists in kwargs")
                kwargs['$'+str(i)] = args[i]

            method = 'GET' if len(kwargs) <= 0 else 'POST'
            nerve.log("remote query: " + method + " " + urlstring, logtype='query')
            # TODO should there be an option to encode the args as json?
            #options = { }
            r = requests.request(method, urlstring, json=None if method == 'GET' else kwargs)

            if r.status_code != 200:
                raise Exception("request to " + urlstring + " failed. " + str(r.status_code) + ": " + r.reason, r.text)

            (mimetype, pdict) = cgi.parse_header(r.headers['content-type'])
            if mimetype == 'application/json':
                return r.json()
            elif mimetype == 'application/x-www-form-urlencoded':
                return urllib.parse.parse_qs(r.text, keep_blank_values=True)
            else:
                return r.text

        else:
            raise Exception("unsupported url scheme: " + url.scheme)

    else:
        path = urllib.parse.unquote_plus(url.path)
        kwargs = nerve.Request.parse_query_args(url, kwargs)
        args = nerve.Request.parse_positional_args(args, kwargs)

        nerve.log("executing query: " + path + " " + repr(args) + " " + repr(kwargs), logtype='query')

        #obj = rootnodes[0].get_object(url.path.lstrip('/'))
        #if callable(obj):
        #    result = obj(*args, **kwargs)
        #else:
        #    result = obj
        result = rootnodes[0].query(path.lstrip('/'), *args, **kwargs)

        rstr = str(result)
        nerve.log("result: " + ( rstr[:75] + '...' if len(rstr) > 75 else rstr ), logtype='debug')
        return result
"""

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
    return _scheme_handlers[scheme](url, *args, **kwargs)


def LocalQueryHandler(_queryurl, *args, **kwargs):
    path = urllib.parse.unquote_plus(_queryurl.path)
    kwargs = nerve.Request.parse_query_args(_queryurl, kwargs)
    args = nerve.Request.parse_positional_args(args, kwargs)

    nerve.log("executing query: " + path + " " + repr(args) + " " + repr(kwargs), logtype='query')

    """
    obj = rootnodes[0].get_object(_queryurl.path.lstrip('/'))
    if callable(obj):
        result = obj(*args, **kwargs)
    else:
        result = obj
    """
    result = rootnodes[0].query(path.lstrip('/'), *args, **kwargs)

    rstr = str(result)
    nerve.log("result: " + ( rstr[:75] + '...' if len(rstr) > 75 else rstr ), logtype='debug')
    return result

register_scheme('local', LocalQueryHandler)


def HTTPQueryHandler(_queryurl, *args, **kwargs):
    # TODO we ignore args and kwargs when querying a http server.  We could automatically make a query string of kwargs, and possible
    #      still ignore args, or we could use a POST request instead, and send the json of the arguments (possible JSON-RPC style)

    nerve.log("executing query: " + _queryurl.path + " " + repr(args) + " " + repr(kwargs), logtype='query')

    # TODO is this valid?  To have query options in the kwargs?  Might that cause problems for some things?  Should the key be deleted here if
    # present, so that it doesn't get encoded.
    #if 'query_method' in kwargs:
    #   method = kwargs['query_method']
    #   del kwargs['query_method']
    #else:
    #   method = 'POST'

    #method = kwargs['query_method'] if 'query_method' in kwargs else 'POST'

    for i in range(len(args)):
        #if '$'+str(i) in kwargs:
        #   raise ValueError("positional argument " + '$'+str(i) + " already exists in kwargs")
        kwargs['$'+str(i)] = args[i]

    method = 'GET' if len(kwargs) <= 0 else 'POST'
    urlstring = urllib.parse.urlunparse((_queryurl.scheme, _queryurl.netloc, _queryurl.path, '', '', ''))
    nerve.log("remote query: " + method + " " + urlstring, logtype='query')
    # TODO should there be an option to encode the args as json?
    #options = { }
    r = requests.request(method, urlstring, json=None if method == 'GET' else kwargs)

    if r.status_code != 200:
        raise Exception("request to " + urlstring + " failed. " + str(r.status_code) + ": " + r.reason, r.text)

    (mimetype, pdict) = cgi.parse_header(r.headers['content-type'])
    if mimetype == 'application/json':
        result = r.json()
    elif mimetype == 'application/x-www-form-urlencoded':
        result = urllib.parse.parse_qs(r.text, keep_blank_values=True)
    else:
        result = r.text

    rstr = str(result)
    nerve.log("result: " + ( rstr[:75] + '...' if len(rstr) > 75 else rstr ), logtype='debug')
    return result

register_scheme('http', HTTPQueryHandler)
register_scheme('https', HTTPQueryHandler)





