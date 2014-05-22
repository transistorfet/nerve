#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import socket
import os
import sys
import signal
import traceback

import cStringIO
import re

import BaseHTTPServer
import ssl

import cgi
import json
import mimetypes

if sys.version.startswith('3'):
    from urllib.parse import parse_qs
else:
    from urlparse import parse_qs


class PyHTMLParser (object):
    def __init__(self, contents):
	self.contents = contents
	self.segments = None
	self.pycode = ''

    def evaluate(self):
	self.parse_segments()
	self.generate_python()
	return self.execute_python()

    def parse_segments(self):
	self.segments = [ ]
	contents = self.contents
        while contents != '':
            first = contents.partition('<%')
            second = first[2].partition('%>')

	    self.segments.append({ 'type' : 'raw', 'data' : first[0] })

	    if second[0]:
		if second[0][0] == '=':
		    self.segments.append({ 'type' : 'eval', 'data' : second[0][1:] })
		else:
		    self.segments.append({ 'type' : 'exec', 'data' : second[0] })

	    contents = second[2]

    def generate_python(self):
	lines = [ ]
	for i, seg in enumerate(self.segments):
	    if seg['type'] == 'raw':
		lines.append("print pyhtml.segments[%d]['data']," % (i,))
	    elif seg['type'] == 'eval':
		lines.append("print eval(pyhtml.segments[%d]['data'])," % (i,))
	    elif seg['type'] == 'exec':
		sublines = seg['data'].split('\n')
		lines.extend(sublines)

	lines = self.fix_indentation(lines)
	self.pycode = '\n'.join(lines)

    def fix_indentation(self, lines):
	indent = 0
	for i in xrange(0, len(lines)):
	    lines[i] = (indent * '  ') + lines[i].lstrip()
	    if re.match('[^#]*:\s*$', lines[i]):
		indent += 1
	    elif lines[i].strip().lstrip().lower() == 'end':
		indent -= 1
		lines[i] = ''

	    # TODO also take into account \ and """ """
	return lines

    def execute_python(self):
	self.globals = { }
	self.globals['nerve'] = nerve
	self.globals['pyhtml'] = self
	old_stdout = sys.stdout
	try:
	    self.output = cStringIO.StringIO()
	    sys.stdout = self.output
	    #print "<pre>\n" + self.pycode + "\n</pre>\n"
	    exec self.pycode in self.globals
	except Exception as e:
	    #print '<b>Eval Error</b>: (line %s) %s<br />' % (str(self.output.getvalue().count('\n') + 1), repr(e))
	    print '\n<b>Eval Error:</b>\n<pre>\n%s</pre><br />\n' % (traceback.format_exc(),)
	finally:
	    sys.stdout = old_stdout
        return self.output.getvalue()
	

class HTTPRequestHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = "Nerve HTTP/0.1"

    def log_message(self, format, *args):
        nerve.log(self.address_string() + ' ' + format % args)

    def check_authorization(self):
	if not self.server.username:
	    return True

        authdata = self.headers.getheader('Authorization')
        if type(authdata).__name__ == 'str':
            authdata = authdata.split(' ')[-1].decode('base64')
            username = authdata.split(':')[0]
            password = authdata.split(':')[1]

            if username == self.server.username and password == self.server.password:
                return True

	self.send_response(401)
	self.send_header('WWW-Authenticate', 'Basic realm="Secure Area"')
	self.send_header('Content-type', 'text/html')
	self.end_headers()
	self.wfile.write('Authorization required.')
        return False

    def send_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('404 Not Found')

    def send_json_headers(self):
	self.send_response(200)
	self.send_header('Content-type', 'application/json')
	self.end_headers()

    def do_GET(self):
        if self.check_authorization() == False:
            return

	# handle commands sent via GET
        if self.path.startswith('/command/'):
	    command = self.path[9:]

	    try:
		command_func = getattr(self.server, 'command_' + self.path[9:])
	    except AttributeError:
		self.send_404()
		return

            self.send_json_headers()
	    ret = command_func()
	    self.wfile.write(json.dumps(ret))
	    return

	if not self.is_valid_path(self.path):
	    self.send_404()
	    return

	filename = self.server.root + '/' + self.path[1:]

	# If the path resolves to a directory, then set the filename to the index.html file inside that directory
	if os.path.isdir(filename):
	    filename = filename.strip('/') + '/index.html'

	# send error if nothing found
	if not os.path.isfile(filename):
	    self.send_404()
	    return

	# server up the file
	(self.mimetype, self.encoding) = mimetypes.guess_type(filename)

	self.send_response(200)
	self.send_header('Content-type', self.mimetype)
	self.end_headers()

	with open(filename, 'r') as f:
	    contents = f.read()

	    if self.mimetype == 'text/html' or self.mimetype == 'text/xml':
		contents = PyHTMLParser(contents).evaluate()
	    self.wfile.write(contents)
	return

    def do_POST(self):
        if self.check_authorization() == False:
            return

	# empty post doesn't provide a content-type.
	ctype = None
        try:
            (ctype, pdict) = cgi.parse_header(self.headers['content-type'])
        except:
	    pass

        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(self.rfile.read(length), keep_blank_values=True)
        else:
            postvars = {}

        self.send_json_headers()

	ret = self.server.handle_post(self.path, postvars)
	self.wfile.write(json.dumps(ret))

    @staticmethod
    def is_valid_path(path):
	if not path[0] == '/':
	    return False
	for name in path.split('/'):
	    if name == '.' or name == '..':
		return False
	return True



class HTTPServer (nerve.Portal, BaseHTTPServer.HTTPServer):

    def __init__(self, port):
	self.root = 'wwwdata'

        self.username = None #obplayer.Config.setting('http_admin_username')
        self.password = None #obplayer.Config.setting('http_admin_password')

        #sslenable = obplayer.Config.setting('http_admin_secure')
        #sslcert = obplayer.Config.setting('http_admin_sslcert')

        #server_address = ('', obplayer.Config.setting('http_admin_port'))  # (address, port)

	BaseHTTPServer.HTTPServer.__init__(self, ('', port), HTTPRequestHandler)
	#if sslenable:
	#    self.socket = ssl.wrap_socket(self.socket, certfile=sslcert, server_side=True)

        sa = self.socket.getsockname()
        nerve.log('starting http(s) on port ' + str(sa[1]))

	self.thread = nerve.Task('HTTPServerTask', target=self.serve_forever)
	self.thread.daemon = True
	self.thread.start()

    def handle_post(self, path, postvars):
	print "Path: " + path
	print "Vars: " + repr(postvars)
	if 'tag' in postvars:
	    #nerve.query(postvars['tag'][0], CallbackPortal(self.handle_query_response))
	    nerve.query(postvars['tag'][0])
	elif path == '/status':
	    player = nerve.get_device('music')
	    if player is not None:
		return player.getstatus(None)

    def handle_query_response(self, msg):
	pass

    """
    def form_item_selected(self, setting, value):
        if obplayer.Config.setting(setting, True) == value:
            return ' selected="selected"'
        else:
            return ''

    def form_item_checked(self, setting):
        if obplayer.Config.setting(setting, True):
            return ' checked="checked"'
        else:
            return ''

    def fullscreen_status(self):
	return 'Off'

    def command_restart(self):
	os.kill(os.getpid(), signal.SIGINT)
	return { 'status' : True }

    def command_fstoggle(self):
	return { 'status' : True, 'fullscreen' : 'Off' }  # + str(not self.Gui.gui_window_fullscreen).lower() + ' }'

    def handle_post(self, path, postvars):
        error = None

	# run through each setting and make sure it's valid. if not, complain.
        for key in postvars:
            settingName = key
            settingValue = postvars[key][0]

            #error = obplayer.Config.validateSetting(settingName, settingValue)

            if error != None:
                return { 'status' : False, 'error' : error }

	# we didn't get an errors on validate, so update each setting now.
        for key in postvars:
            settingName = key
            settingValue = postvars[key][0]
            #obplayer.Config.set(settingName, settingValue)

        return { 'status' : True }
    """

