#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve
import nerve.connect

import io
import json
import time
import os.path
import traceback
import mimetypes
import urllib.parse


def delistify(kwargs):
    for name in kwargs.keys():
        if not name.endswith("[]") and isinstance(kwargs[name], list) and len(kwargs[name]) == 1:
            kwargs[name] = kwargs[name][0]
    return kwargs


class Request (object):
    def __init__(self, source, user, reqtype, urlstring, args, headers=dict()):
        self.source = source
        self.user = user
        self.reqtype = reqtype      # could be GET, POST, QUERY, CONNECT?
        self.url = urllib.parse.urlparse(urlstring) if type(urlstring) == str else urlstring
        self.args = self.parse_query_args(self.url, args)
        self.headers = [ (key.lower(), item) for (key, item) in headers.items() ]

        self.segments = self.url.path.lstrip('/').split('/')
        self.current_segment = 0

    @staticmethod
    def parse_query_args(url, kwargs=None):
        if not kwargs:
            kwargs = dict()
        kwargs.update(delistify(urllib.parse.parse_qs(url.query, keep_blank_values=True)))
        return kwargs

    @staticmethod
    def parse_positional_args(args, kwargs):
        args = list(args)
        for i in sorted( int(key[1:]) for key in kwargs.keys() if key.startswith('$') ):
            if i != len(args):
                raise ValueError("incorrectly numbered positional argument: $" + str(i))
            args.append(kwargs['$' + str(i)])
            del kwargs['$' + str(i)]
        return args

    def arg(self, name, default=None):
        if name in self.args:
            return self.args[name]
        return default

    def get_header(self, name, default=None):
        name = name.lower()
        for key, value in self.headers:
            if key == name:
                return value
        return default

    def get_header_all(self, name):
        name = name.lower()
        return [ value for key, value in self.headers if key == name ]

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

    def get_slug(self):
        if self.current_segment < len(self.segments):
            seg = '/'.join(self.segments[self.current_segment:])
            self.current_segment = len(self.segments)
            return seg
        return ''

    def get_host(self):
        host = self.get_header('Host', default=None)
        if host == None:
            host = 'localhost:' + str(self.source.get_setting('port'))
        return host

    def get_location(self, leaf=''):
        location = '/' + '/'.join(self.segments[:self.current_segment-1])
        if leaf:
            location += '/' + leaf
        return location

    def make_url(self, leaf=''):
        return 'http://' + self.get_host() + self.get_location(leaf)


class NotFoundError (Exception): pass
class ControllerError (Exception): pass


class Controller (nerve.ObjectNode):
    def __init__(self, **config):
        super().__init__(**config)
        self._headers = [ ]
        self._redirect = None
        self._error = None
        self._view = None
        self._request = None

    def initialize(self, request):
        self._headers = [ ]
        self._redirect = None
        self._error = None
        self._view = None
        self._request = request

    def finalize(self, request):
        pass

    def add_header(self, name, value):
        self._headers.append( (name, value) )

    def get_headers(self):
        return self._headers

    def set_view(self, view):
        self._view = view

    def load_plaintext_view(self, text):
        self.set_view(PlainTextView(text))

    def load_json_view(self, data):
        self.set_view(JsonView(data))

    def load_file_view(self, filename, base=None):
        self.set_view(FileView(filename, base))

    def get_mimetype(self):
        if not self._view:
            return None
        return self._view._mimetype

    def get_output(self):
        if not self._view:
            return None
        return self._view.get_output()

    def redirect_to(self, location):
        self._redirect = location

    def get_redirect(self):
        return self._redirect

    def set_error(self, error):
        self._error = error

    def get_error(self):
        return self._error

    def get_request(self):
        return self._request

    def handle_request(self, request):
        self.initialize(request)
        try:
            self.do_request(request)
            if self._view:
                self._view.finalize()

        except Exception as e:
            try:
                self.handle_error(e, traceback.format_exc(), request)
            except:
                nerve.log("error while handling exception:\n" + traceback.format_exc(), logtype='error')

        finally:
            self.finalize(request)

        if self._error is None:
            return True
        return False

    def handle_error(self, error, traceback, request):
        self.set_error(error)
        if not self._view:
            self.load_plaintext_view('')
        nerve.log(traceback, logtype='error')
        #if 'text/html' in request.headers['accept']:
        #   render some html
        #else:
        #   self.write(traceback)
        self._view.write(traceback)

    def do_request(self, request):
        name = request.next_segment()
        if not name:
            name = 'index'

        try:
            method = getattr(self, name)
        except AttributeError:
            raise NotFoundError("Page not found: " + name) from None

        # TODO this should be added to make accessible only methods declared as public, but the permissions error causes a login prompt to show which we don't want in this case because no matter who
        #      tries to access the method, it should be denied
        if not nerve.is_public(method):
            raise nerve.users.UserPermissionsError("method is not public: " + name)
        method(request)


class View (nerve.ObjectNode):
    def __init__(self, **config):
        super().__init__(**config)
        self._mimetype = None
        self._encoding = 'utf-8'
        self._finalized = False
        self._output = None

    def get_mimetype(self):
        return (self._mimetype, self._encoding)

    def set_output(self, output):
        self._output = output

    def get_output(self):
        self.finalize()
        if self._output:
            return self._output
        return b''

    def __str__(self):
        self.finalize()
        if self._output:
            return self._output.decode(self._encoding)
        return "<no output>"

    def finalize(self):
        if not self._finalized:
            self._finalized = True
            self.render()

    def render(self):
        pass


class TextView (View):
    def __init__(self, **config):
        super().__init__(**config)
        self._output = io.StringIO()

    def write_bytes(self, data):
        self._output.write(data.decode(self._encoding))

    def write(self, text):
        self._output.write(text)

    def print(self, *args, **kwargs):
        kwargs['file'] = self._output
        print(*args, **kwargs)

    def get_output(self):
        self.finalize()
        return bytes(self._output.getvalue(), self._encoding)

    def __str__(self):
        self.finalize()
        return self._output.getvalue()


class PlainTextView (TextView):
    def __init__(self, text=None):
        super().__init__()
        self._mimetype = 'text/plain'
        if text != None:
            self.write(text)


class HTMLView (TextView):
    def __init__(self, **config):
        super().__init__(**config)
        self._mimetype = 'text/html'
        self._indent = 0

    def write(self, text, tab=0):
        if tab < 0:
            self._indent += tab
        super().write(('    ' * self._indent) + text)
        if tab > 0:
            self._indent += tab

    def writeln(self, text, tab=0):
        self.write(text + '\n', tab)


class JsonView (View):
    def __init__(self, data=None):
        super().__init__()
        self._mimetype = 'application/json'
        self._data = data

    def render(self):
        def json_default(obj):
            return str(obj)
        text = json.dumps(self._data, sort_keys=True, indent=4, separators=(',', ': '), default=json_default)
        self.set_output(bytes(text, self._encoding))


class FileView (View):
    def __init__(self, filename, base=None):
        super().__init__()
        self.filename = os.path.join(base, filename) if base else filename

    def render(self):
        (self._mimetype, self._encoding) = mimetypes.guess_type(self.filename)
        if self._encoding == None:
            self._encoding = 'utf-8'
        with open(self.filename, 'rb') as f:
            contents = f.read()
            self.set_output(contents)


@nerve.types.RegisterConfigType('view')
class ViewConfigType (nerve.types.StrConfigType):
    pass


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
        config_info.add_setting('controllers', "Controllers", default=dict(), itemtype='object(core/Controller)', weight=1)
        #config_info.add_setting('template', "Default Template", datatype='object', weight=1, default=dict(__type__='http/views/template/TemplateView'))
        config_info.add_setting('template', "Default Template", datatype='object', weight=1, default=dict())
        return config_info

    def get_setting(self, name, typename=None):
        setting = super().get_setting(name, typename)
        if setting:
            return setting
        if name == 'parent':
            return None
        parentname = self.get_setting('parent')
        if not parentname:
            return None
        try:
            parent = nerve.get_object(parentname)
        except AttributeError:
            return None
        return parent.get_setting(name, typename)

    def start_server(self):
        raise NotImplementedError

    def stop_server(self):
        raise NotImplementedError

    def make_controller(self, request):
        controllers = self.get_setting('controllers')
        """
        if not controllers:
            parentname = self.get_setting('parent')
            if parentname:
                parent = nerve.get_object(parentname)
                controllers = parent.get_setting('controllers')
        """

        if not controllers:
            return None
        return self.make_controller_static(request, controllers)

    @staticmethod
    def make_controller_static(request, controllers):
        basename = request.next_segment()
        if basename in controllers:
            controller = controllers[basename]
        else:
            request.back_segment();
            controller = controllers['__default__']
        return nerve.Module.make_object(controller['__type__'], controller)


class Model (nerve.ObjectNode):
    pass


class Device (Model):
    def __init__(self, **config):
        super().__init__(**config)
        self._callbacks = { }

    def on_update(self, attrib, func):
        self._callbacks[attrib] = func


class PyCodeQuery (nerve.ObjectNode):
    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('code', "Python Code", default='', datatype='textarea')
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


