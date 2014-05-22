#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import os.path

class LayoutDevice (nerve.Device):
    def _get_file_contents(self, filename):
	with open(filename, 'r') as f:
	    data = f.read()
	return data

    def dispatch(self, msg, index=0):
	if index + 1 != len(msg.names):
	    raise nerve.InvalidRequest(msg.query)
	filename = 'layouts/' + msg.names[index] + ".xml"
	if os.path.isfile(filename):
	    contents = self._get_file_contents(filename)
	    msg.from_port.send(msg.query + " " + contents)
	else:
	    raise Exception("In " + msg.query + ": File not found: " + filename)

