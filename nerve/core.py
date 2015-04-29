#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import io
import json
import time
import traceback
import mimetypes
import urllib.parse


class Request (object):
    def __init__(self, server, reqtype, urlstring, args):
        self.server = server
        self.reqtype = reqtype
        (self.url, self.args) = self.parse_query(urlstring, args)

        self.segments = self.url.path.lstrip('/').split('/')
        self.current_segment = 0

    @staticmethod
    def parse_query(urlstring, args=None):
        if not args:
            args = dict()
        url = urllib.parse.urlparse(urlstring)
        args.update(urllib.parse.parse_qs(url.query, keep_blank_values=True))
        for name in args.keys():
            if not name.endswith("[]") and isinstance(args[name], list) and len(args[name]) == 1:
                args[name] = args[name][0]
        return (url, args)

    def next_segment(self):
        if self.current_segment < len(self.segments):
            seg = self.segments[self.current_segment]
            self.current_segment += 1
            return seg
        return ''

    def back_segment(self):
        if self.current_segment > 0:
            self.current_segment -= 1

    def remaining_segments(self):
        if self.current_segment < len(self.segments):
            seg = '/'.join(self.segments[self.current_segment:])
            self.current_segment = len(self.segments)
            return seg
        return ''

    def arg(self, name, default=None):
        if name in self.args:
            return self.args[name]
        return default


class Controller (nerve.ObjectNode):
    def __init__(self, **config):
        nerve.ObjectNode.__init__(self, **config)
        self.error = None
        self.redirect = None
        self.output = None

    def initialize(self):
        self.error = None
        self.redirect = None
        self.mimetype = 'text/plain'
        self.output = io.BytesIO()

    def finalize(self):
        pass

    def set_mimetype(self, mimetype):
        if len(self.output.getvalue()) > 0:
            raise Exception('mimetype', "in nerve.Controller, attempting to change mimetype after output has been written")
        self.mimetype = mimetype

    def report_error(self, typename, message):
        self.error = Exception(typename, message)

    def redirect_to(self, location):
        self.redirect = location

    def write_bytes(self, data):
        self.output.write(data)

    def write_text(self, data):
        self.output.write(data.encode('utf-8'))

    def write_json(self, data):
        self.mimetype = 'application/json'
        def json_default(obj):
            return str(obj)
        text = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '), default=json_default)
        self.write_text(text)

    def write_file(self, filename):
        (mimetype, encoding) = mimetypes.guess_type(filename)
        self.set_mimetype(mimetype)
        with open(filename, 'rb') as f:
            contents = f.read()
            self.write_bytes(contents)

    def get_mimetype(self):
        return self.mimetype

    def get_error(self):
        return self.error

    def get_redirect(self):
        return self.redirect

    def get_output(self):
        return self.output.getvalue()

    def handle_request(self, request):
        self.initialize()
        try:
            self.do_request(request)
        except:
            tb = traceback.format_exc()
            nerve.log(tb)
            self.write_text(tb)
            self.report_error('internal', tb)
        finally:
            self.finalize()

        if self.error is None:
            return True
        return False

    def do_request(self, request):
        name = request.next_segment()
        if not name:
            name = 'index'
        func = getattr(self, name)
        func(request)


class Server (nerve.ObjectNode):
    def __init__(self, **config):
        nerve.ObjectNode.__init__(self, **config)

    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        config_info.add_setting('parent', "Parent Server", default='')
        """
        servers = nerve.get_object('/servers')
        if servers:
            for option in servers.keys():
                config_info.add_option('parent', option, '/servers/' + option)
        """
        config_info.add_setting('controllers', "Controllers", default=dict())
        return config_info

    def add_controller(self, name, controller):
        self.controllers[name] = controller

    def start_server(self):
        pass

    def stop_server(self):
        pass

    def make_controller(self, request):
        controllers = self.get_setting('controllers')
        if not controllers:
            parentname = self.get_setting('parent')
            if parentname:
                parent = nerve.get_object(parentname)
                controllers = parent.get_setting('controllers')

        if not controllers:
            return None

        basename = request.next_segment()
        if basename in controllers:
            controller = controllers[basename]
        else:
            request.back_segment();
            controller = controllers['__default__']
        return nerve.ObjectNode.make_object(controller['__type__'], controller)


class Model (nerve.ObjectNode):
    pass


class Device (Model):
    def __init__(self, **config):
        nerve.ObjectNode.__init__(self, **config)
        self.callbacks = { }

    def on_update(self, attrib, func):
        self.callbacks[attrib] = func

    """
    def query(self, ref, *args, **kwargs):
        (name, sep, remain) = ref.partition('.')
        if name and name[0] == '_':
            raise AttributeError("cannot access underscore attributes through a query: '" + name + "'")
        if remain:
            dev = getattr(self, name)
            return dev.query(remain, *args, **kwargs)
        else:
            func = getattr(self, name)
            return func(*args, **kwargs)
    """


# TODO is this not redundant with objects/SymbolicLink
class AliasDevice (Device):
    def __init__(self, **config):
        Device.__init__(self, **config)

    def __getattr__(self, name):
        pass


class SingleQuery (nerve.ObjectNode):
    @staticmethod
    def get_config_info():
        config_info = nerve.ObjectNode.get_config_info()
        config_info.add_setting('code', "Python Code", default='')
        return config_info

    def __call__(self, *args):
        code = self.get_setting('code')
        exec(code)


