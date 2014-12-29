#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import json
import traceback
import cStringIO

from urlparse import parse_qs,urlparse
# TODO for python3
#from urllib.parse import parse_qs,urlparse


class Request (object):
    def __init__(self, server, reqtype, urlstring, args):
	self.server = server
	self.reqtype = reqtype
	# TODO you could do urlparse here
	self.url = urlparse(urlstring)
	self.segments = self.url.path.lstrip('/').split('/')
	self.current_segment = 0
	self.args = args

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
	    if name.endswith("[]"):
		return self.args[name]
	    else:
		return self.args[name][0]
	return default


class RedirectException (Exception):
    pass


class Controller (nerve.ConfigObject):
    def __init__(self, **config):
	nerve.ConfigObject.__init__(self, **config)
	self.error = None
	self.output = None

    def initialize(self):
	self.error = None
	self.mimetype = 'text/plain'
	self.output = cStringIO.StringIO()

    def finalize(self):
	pass

    def set_mimetype(self, mimetype):
	if len(self.output.getvalue()) > 0:
	    raise Exception('mimetype', "in nerve.Controller, attempting to change mimetype after output has been written")
	self.mimetype = mimetype

    def get_mimetype(self):
	return self.mimetype

    def write_output(self, data):
	self.output.write(data)

    def write_json(self, data):
	self.mimetype = 'application/json'
	self.output.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

    def write_error(self, typename, message):
	self.error = Exception(typename, message)

    def get_output(self):
	return self.output.getvalue()

    def handle_request(self, request):
	self.initialize()
	try:
	    self.do_request(request)
	except RedirectException as redirect:
	    self.error = redirect
	except:
	    nerve.log(traceback.format_exc())
	    # TODO this should change when you get a better error reporting system
	    self.write_error('internal', traceback.format_exc())
	    self.write_output(traceback.format_exc())
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
	return func(request)


class Server (nerve.ConfigObject):
    def __init__(self, **config):
	nerve.ConfigObject.__init__(self, **config)
	if 'controllers' not in config:
	    self.controllers = { }
	else:
	    self.controllers = self.make_object_table(config['controllers'])

    @staticmethod
    def get_defaults():
	defaults = nerve.ConfigObject.get_defaults()
	defaults['controllers'] = { }
	return defaults

    def get_config_data(self):
	config = nerve.ConfigObject.get_config_data(self)
	config['controllers'] = self.save_object_table(self.controllers)
	return config

    def add_controller(self, name, controller):
	self.controllers[name] = controller

    def start_server(self):
	pass

    def stop_server(self):
	pass

    def find_controller(self, request):
	basename = request.next_segment()
	if basename in self.controllers:
	    controller = self.controllers[basename]
	else:
	    request.back_segment();
	    controller = self.controllers['__default__']
	return controller


class Device (nerve.ConfigObject):
    device_types = { }

    def __init__(self, **config):
	nerve.ConfigObject.__init__(self, **config)

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

    @staticmethod
    def register_device_type(name, device_class, description):
	Device.device_types[name] = { 'class' : device_class, 'description' : description }
	# TODO you could call a static method on the class to get config data...



#def query(ref, **kwargs):
#    return root.query(ref, **kwargs)

#root = NewDevice()

"""

root = NewDevice()
root.medialib = MediaLib()
root.rgb = NerveSerialDevice("/dev/ttyACM1", 19200)
root.stereo = Stereo(root.rgb)

media_list = medialib.get_media_list(...)

class Player (object):
    def play(self, **kwargs):
	# play the thing

    def get_song(self, **kwargs):
	return song_name	# this would get encoded to json if it was going back to webside

    def play_song(self, **kwargs):
	if len(kwargs) != 1 or 'url' not in kwargs:
	    return { 'error' : "method takes 1 argument: url" }
	# play song specified in kwargs['url']

# so you can totally do
songname = player.get_song()
# or
player.play_song(url='afile.mp3')

# but you can't do
player.play_song('afile.mp3')		# (unless you do some trickery...)

# you should also have a method of doing...
nerve.query('player.play_song', { 'url' : 'afile.mp3' })
# which should be identical


portals = something
portals.http = nerve.http.HTTPServer(8888)
portals.console = nerve.Console()

# sortof, but there maybe should be a list of devices and portals so they aren't confused (like the existing stuff)


"""






import Queue
import time

class Something (object):
    dispatch_queue = Queue.PriorityQueue()

    @staticmethod
    #def request(url, *args, delay=0, callback=None):
    def request(url, args, delay=0, callback=None):
	entry = (time.time() + delay, url, args, callback)
	Something.dispatch_queue.put(entry)


    def dispatch_request(self, url, args):
	urldata = urlparse.urlparse(url)
	# TODO do all the rest

    def run(self):
	while not self.thread.stopflag.wait(1):
	    try:
		entry = Something.dispatch_queue.get(True, 1.0)

		## If the next entry is scheduled for the future, then put it back and wait a bit
		if time.time() > entry[0]:
		    Something.dispatch_queue.put(entry)
		    time.sleep(0.1)

		## Otherwise, disptach the request
		else:
		    result = self.disptach_request(entry[1], entry[2])
		    if entry[3] is not None:
			entry[3](result)

		Something.dispatch_queue.task_done()
	    except queue.Empty as e:
		pass

class AliasDevice (Device):
    def __init__(self, portal, uri):
	pass

    def dispatch(self, msg, index=0):
	pass

