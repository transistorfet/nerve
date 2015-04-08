#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import os
import sys
import traceback

import io
import re

import cgi
import json
import mimetypes

import urllib.parse


class PyHTML (object):
    version = '0.2'

    def __init__(self, filename, request, data=None):
        self.segments = None
        self.contents = ''
        self.pycode = ''

        if data is None:
            data = { }
        self.data = data

        self._FILENAME = filename
        self._PATH = request.url.path if request else ''
        self._REQUEST = request

        self._POST = { }
        self._GET = { }
        if request:
            if request.reqtype == "GET":
                self._GET = request.args
            elif reqtype == "POST":
                self._POST = request.args

    def ARGS(self, name, default='', as_array=False):
        if not self._REQUEST or name not in self._REQUEST.args:
            return default
        if as_array is False:
            return self._ARGS[name][0]
        else:
            return self._ARGS[name]

    def GET(self, name, default='', as_array=False):
        if name not in self._GET:
            return default
        if as_array is False:
            return self._GET[name][0]
        else:
            return self._GET[name]

    def POST(self, name, default='', as_array=False):
        if name not in self._POST:
            return default
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
        with open(self._FILENAME, 'r') as f:
            self.contents = f.read()

        self.segments = self._parse_segments()
        lines = [ ]
        for i, seg in enumerate(self.segments):
            if seg['type'] == 'raw':
                lines.append("py.output.write(py.segments[%d]['data'])" % (i,))
            elif seg['type'] == 'eval':
                lines.append("py.output.write(str(eval(py.segments[%d]['data'])))" % (i,))
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

            segments.append({ 'type' : 'raw', 'data' : first[0] if len(first[0]) > 0 and first[0][-1] == '\n' else first[0].rstrip(' \t') })

            if second[0]:
                if second[0][0] == '=':
                    segments.append({ 'type' : 'eval', 'data' : second[0][1:] })
                else:
                    segments.append({ 'type' : 'exec', 'data' : second[0] })

            if len(second[2]) > 0 and second[2][0] == '\n':
                contents = second[2][1:]
            else:
                contents = second[2]
        return segments

    def _fix_indentation(self, lines):
        indent = 0
        for i in range(0, len(lines)):
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
            elif code.lower() == 'end':
                indent -= 1
                lines[i] = ''
            else:
                lines[i] = (indent * '  ') + lines[i].lstrip()
        return lines

    def execute_python(self):
        old_stdout = sys.stdout

        try:
            self.output = io.StringIO()
            sys.stdout = self.output

            self.globals = self.data
            self.globals['nerve'] = nerve
            self.globals['py'] = self
            self.globals['json'] = json
            self.globals['re'] = re
            self.globals['urlencode'] = urllib.parse.quote
            self.globals['urldecode'] = urllib.parse.unquote
            self.globals['echo'] = self.output.write

            #self.debug_print_env()
            exec(self.pycode, self.globals)

        except Exception as e:
            #print ('<b>Eval Error</b>: (line %s) %s<br />' % (str(self.output.getvalue().count('\n') + 1), repr(e)))
            print ('\n<b>Eval Error:</b>\n<pre>\n%s</pre><br />\n' % (traceback.format_exc(),))
            print ('<br /><pre>' + self.htmlspecialchars('\n'.join([ str(num + 1) + ':  ' + line for num,line in enumerate(self.pycode.splitlines()) ])) + '</pre>')

        finally:
            sys.stdout = old_stdout

        return self.output.getvalue()

    def debug_print_env(self):
        #print ("<pre>\n")
        #for s in self.segments:
        #    print (self.htmlspecialchars(repr(s)))
        #print ("\n</pre><br />\n")

        #print ("<table>\n")
        #for s in self.segments:
        #    print ("<tr><td>" + s['type'] + "</td><td>" + self.htmlspecialchars(repr(s['data'])) + "</td></tr>")
        #print ("\n</table><br />\n")

        print ("<pre>\n" + self.htmlspecialchars(self.pycode) + "\n</pre>\n")
        

