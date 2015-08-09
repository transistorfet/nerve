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
    def __init__(self, server, user, reqtype, urlstring, args, headers=dict()):
        self.server = server
        self.user = user
        self.reqtype = reqtype
        (self.url, self.args) = self.parse_query(urlstring, args)
        self.headers = { key.lower(): item for (key, item) in headers.items() }

        self.segments = self.url.path.lstrip('/').split('/')
        self.current_segment = 0

    @staticmethod
    def parse_query(urlstring, kwargs=None):
        if not kwargs:
            kwargs = dict()
        url = urllib.parse.urlparse(urlstring)
        kwargs.update(urllib.parse.parse_qs(url.query, keep_blank_values=True))
        # TODO should you only do this on the arguments received in the query string, and not all kwargs?
        for name in kwargs.keys():
            if not name.endswith("[]") and isinstance(kwargs[name], list) and len(kwargs[name]) == 1:
                kwargs[name] = kwargs[name][0]
        return (url, kwargs)

    def arg(self, name, default=None):
        if name in self.args:
            return self.args[name]
        return default

    def get_header(self, name, default=None):
        name = name.lower()
        if name in self.header:
            return self.header[name]
        return default

    def next_segment(self, default=None):
        if self.current_segment < len(self.segments):
            seg = self.segments[self.current_segment]
            self.current_segment += 1
            return seg
        return default

    def back_segment(self):
        if self.current_segment > 0:
            self.current_segment -= 1

    def segments_left(self):
        return len(self.segments) - self.current_segment

    def get_remaining_segments(self):
        if self.current_segment < len(self.segments):
            seg = '/'.join(self.segments[self.current_segment:])
            self.current_segment = len(self.segments)
            return seg
        return ''


class NotFoundError (Exception): pass

class ControllerError (Exception): pass


class Controller (nerve.ObjectNode):
    def __init__(self, **config):
        super().__init__(**config)
        self._error = None
        self._redirect = None
        self._output = None

    def initialize(self):
        self._error = None
        self._redirect = None
        #self._mimetype = 'text/plain'
        self._mimetype = None
        self._output = io.BytesIO()

    def finalize(self):
        pass

    def set_mimetype(self, mimetype):
        if len(self._output.getvalue()) > 0:
            raise Exception('mimetype', "in nerve.Controller, attempting to change mimetype after output has been written")
        self._mimetype = mimetype

    def redirect_to(self, location):
        self._redirect = location

    def write_bytes(self, data):
        self._output.write(data)

    def write_text(self, data):
        self._output.write(data.encode('utf-8'))

    def write_json(self, data):
        self._mimetype = 'application/json'
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
        return self._mimetype

    def get_error(self):
        return self._error

    def get_redirect(self):
        return self._redirect

    def get_output(self):
        return self._output.getvalue()

    def handle_request(self, request):
        self.initialize()
        try:
            self.do_request(request)

        except Exception as e:
            self._error = e
            try:
                self.handle_error(self._error, traceback.format_exc())
            except:
                nerve.log("error while handling exception:\n" + traceback.format_exc())

        finally:
            self.finalize()

        if self._error is None:
            return True
        return False

    def handle_error(self, error, traceback):
        if not self._mimetype:
            self._mimetype = 'text/plain'
        nerve.log(traceback)
        #if 'text/html' in request.headers['accept']:
        #   render some html
        #else:
        #   self.write_text(traceback)
        self.write_text(traceback)

    def do_request(self, request):
        name = request.next_segment()
        if not name:
            name = 'index'

        try:
            func = getattr(self, name)
        except AttributeError:
            raise NotFoundError("Page not found: " + name) from None

        func(request)


class View (object):
    def get_output(self):
        raise NotImplementedError


class Server (nerve.ObjectNode):
    servers = [ ]

    def __init__(self, **config):
        super().__init__(**config)
        Server.servers.append(self)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('parent', "Parent Server", default='')
        """
        servers = nerve.get_object('/servers')
        if servers:
            for option in servers.keys():
                config_info.add_option('parent', option, '/servers/' + option)
        """
        config_info.add_setting('controllers', "Controllers", default=dict())
        return config_info

    def start_server(self):
        raise NotImplementedError

    def stop_server(self):
        raise NotImplementedError

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
        super().__init__(**config)
        self._callbacks = { }

    def on_update(self, attrib, func):
        self._callbacks[attrib] = func


class PyExecQuery (nerve.ObjectNode):
    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('code', "Python Code", default='')
        return config_info

    def __call__(self, *args):
        code = self.get_setting('code')
        exec(code)


class SymbolicLink (nerve.ObjectNode):
    def __init__(self, **config):
        super().__init__(**config)

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('target', "Target", default="")
        return config_info

    def __call__(self, *args, **kwargs):
        target = self.get_setting('target')
        #return target(*args, **kwargs)
        return nerve.query(target, *args, **kwargs)

    def get_child(self, index):
        target = self.get_setting('target')
        return SymbolicLink(target=target + '/' + index)

    def set_child(self, index, obj):
        target = self.get_setting('target')
        nerve.set_object(target + '/' + index, obj)


