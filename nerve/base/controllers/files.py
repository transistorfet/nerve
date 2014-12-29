#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve
from nerve.http import PyHTML

import os.path
import mimetypes

class FileController (nerve.Controller):
    def __init__(self, **config):
	nerve.Controller.__init__(self, **config)
	self.root = config['root']

    @staticmethod
    def get_defaults():
	defaults = nerve.Controller.get_defaults()
	defaults['root'] = 'nerve/http/wwwdata'
	return defaults

    def do_request(self, request):
	filename = os.path.join(self.root, request.remaining_segments())

	if os.path.isdir(filename):
	    filename = os.path.join(filename, "index.html")

	if not os.path.isfile(filename):
	    self.write_output("Error file not found: " + filename)
	    return False

	(_, _, extension) = filename.rpartition('.')

	if extension == 'pyhtml':
	    self.set_mimetype('text/html')
	    engine = PyHTML(filename, request)
	    contents = engine.evaluate()
	else:
	    (mimetype, encoding) = mimetypes.guess_type(filename)
	    self.set_mimetype(mimetype)
	    with open(filename, 'r') as f:
		contents = f.read()

	self.write_output(contents)
	return True


