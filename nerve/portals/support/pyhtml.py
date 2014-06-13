#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import traceback

import cStringIO
import re

import cgi
import json
import mimetypes

import urllib

def utf8(data):
    if isinstance(data, unicode):
	return data.encode('utf-8')
    return str(data)

class PyHTMLParser (object):
    def __init__(self, contents, filename=None, reqtype=None, path=None, params=None):
	self.segments = None
	self.pycode = ''
	self.contents = contents

	self._FILENAME = filename
	self._REQTYPE = reqtype
	self._PATH = path
	self._ARGS = params

	if reqtype == "GET":
	    self._GET = params
	    self._POST = { }
	elif reqtype == "POST":
	    self._GET = { }
	    self._POST = params

    def ARGS(self, name, as_array=False):
	if name not in self._ARGS:
	    return ''
	if as_array is False:
	    return self._ARGS[name][0]
	else:
	    return self._ARGS[name]

    def GET(self, name, as_array=False):
	if name not in self._GET:
	    return ''
	if as_array is False:
	    return self._GET[name][0]
	else:
	    return self._GET[name]

    def POST(self, name, as_array=False):
	if name not in self._POST:
	    return ''
	if as_array is False:
	    return self._POST[name][0]
	else:
	    return self._POST[name]

    def htmlspecialchars(self, text):
	return cgi.escape(text, True)

    ### Parser and Execution Code ###

    def evaluate(self):
	self.generate_python()
	return self.execute_python()

    def generate_python(self):
	self.segments = self._parse_segments()
	lines = [ ]
	for i, seg in enumerate(self.segments):
	    if seg['type'] == 'raw':
		lines.append("py.output.write(py.segments[%d]['data'])" % (i,))
	    elif seg['type'] == 'eval':
		lines.append("py.output.write(utf8(eval(py.segments[%d]['data'])))" % (i,))
	    elif seg['type'] == 'exec':
		sublines = seg['data'].split('\n')
		lines.extend(sublines)

	lines = self._fix_indentation(lines)
	self.pycode = '\n'.join(lines)

    def _parse_segments(self):
	segments = [ ]
	contents = self.contents
        while contents != '':
            first = contents.partition('<%')
            second = first[2].partition('%>')

	    segments.append({ 'type' : 'raw', 'data' : first[0] })

	    if second[0]:
		if second[0][0] == '=':
		    segments.append({ 'type' : 'eval', 'data' : second[0][1:] })
		else:
		    segments.append({ 'type' : 'exec', 'data' : second[0] })

	    contents = second[2]
	return segments

    def _fix_indentation(self, lines):
	indent = 0
	for i in xrange(0, len(lines)):
	    code, sep, comment = lines[i].partition('#')
	    code = code.strip()
	    # TODO also take into account \ and """ """, [ ], { }, etc
	    #quote_i = code.find("\"\"\"")

	    if code.endswith(':'):
		found = False
		for kw in [ 'elif', 'else', 'except', 'finally' ]:
		    if code.startswith(kw):
			found = True
			break
		if not found:
		    indent += 1
		lines[i] = ((indent - 1) * '  ') + lines[i].lstrip()
		print lines[i]

	    elif code.lower() == 'end':
		indent -= 1
		lines[i] = ''
	    else:
		lines[i] = (indent * '  ') + lines[i].lstrip()
	return lines

    def execute_python(self):
	self.globals = { }
	self.globals['nerve'] = nerve
	self.globals['py'] = self
	self.globals['urlencode'] = urllib.quote
	self.globals['urldecode'] = urllib.unquote
	self.globals['utf8'] = utf8
	old_stdout = sys.stdout
	try:
	    self.output = cStringIO.StringIO()
	    sys.stdout = self.output
	    self.globals['echo'] = self.output.write
	    self.debug_print_env()
	    exec self.pycode in self.globals
	except Exception as e:
	    #print '<b>Eval Error</b>: (line %s) %s<br />' % (str(self.output.getvalue().count('\n') + 1), repr(e))
	    print '\n<b>Eval Error:</b>\n<pre>\n%s</pre><br />\n' % (traceback.format_exc(),)
	finally:
	    sys.stdout = old_stdout
        return self.output.getvalue()

    def debug_print_env(self):
	#print "<pre>\n"
	#for s in self.segments:
	#    print self.htmlspecialchars(repr(s))
	#print "\n</pre><br />\n"
	print "<pre>\n" + self.htmlspecialchars(self.pycode) + "\n</pre>\n"
	

