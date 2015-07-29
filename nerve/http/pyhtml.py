#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""

PyHTML - HTML with Embedded Python:

The following code will take a filename (or string contents) containing HTML
with embedded tags (<% %>) surronding python code.  When .evaluate() is
called on the object, it will parse out the embedded tags, execute the python
code and assemble the resulting output into a pure HTML file that can then be
sent to the browser.

It first parses the input code into segments which are either HTML (anything
outside the <% %> tags) and python code, retaining the order in which they
appear in the input code.  It then iterates through each segment and produces
appropriate python code.  HTML segments are turned into print statements which
print the HTML code itself.  Special evaluate tags are turned into
print(eval()) statements, which print the evaluated result of the python code.
For normal tags, the code itself is added as-is to the python code being
generated.

The generated python code is then further processed to normalize the
indentation.  When an open block statement is found (such as 'if', 'while',
'for', etc), it will indent all subsequent lines until it reaches an 'end'
keyword on a single line by itself.  If an 'else', 'elif', 'except', or
'finally' keyword is found, it will close the current indentation and start
a new one, without the need for an 'end' keyword for each block.

Once the python code is generated, it is sent to exec(), along with a
dictionary of data arguments passed to the PyHTML object when it's created.
They are added to the global variable dict that is sent to exec().  Numerous
libraries are automatically imported into the global variable dict for
convenience.

The <%= %> special tag will cause the contents of the tag to be passed
to eval(), which will then be printed to the output.  This is a short
hand way of outputting the contents of a variable for example.

The <%%include %> special tag will interpret the contents tag to be a file
name.  It will open the referenced file, parse the contents into the
python code currently being generated, and execute it as one big script
after all include tags have been processed.  It uses the current working
directory as the relative root.

BUGS:
- currently does not support multi-line comments using triple double-quotes
- seems to complain if a normal python tag contains no actual code, only comments

"""

import nerve

import os
import sys
import time
import traceback

import io
import re

import cgi
import json
import mimetypes

import urllib
import urllib.parse


class PyHTML (object):
    version = '0.3'

    def __init__(self, request, data=None, filename=None, code=None):
        self._contents = ''
        self._segments = [ ]
        self._pycode = ''
        self._output = None
        self._start_time = 0

        self.FILENAME = filename
        self.REQUEST = request
        self.PATH = request.url.path if request else ''

        if data is None:
            data = { }
        self._data = data
        self._init_globals()

        if code is not None:
            self._contents = code
        elif filename is not None:
            self._contents = self._read_contents(filename)

    def ARGS(self, name, default='', as_array=False):
        if not self.REQUEST or name not in self.REQUEST.args:
            return default
        if as_array is False:
            return self.REQUEST.args[name][0]
        else:
            return self.REQUEST.args[name]

    def GET(self, name, default='', as_array=False):
        if not self.REQUEST or self.REQUEST.reqtype != "GET":
            return default
        return self.ARGS(name, default, as_array)

    def POST(self, name, default='', as_array=False):
        if not self.REQUEST or self.REQUEST.reqtype != "POST":
            return default
        return self.ARGS(name, default, as_array)

    def _init_globals(self):
        self._globals = self._data
        self._globals['nerve'] = nerve
        self._globals['py'] = self

        self._globals['json'] = json
        self._globals['re'] = re
        self._globals['time'] = time
        self._globals['urllib'] = urllib
        self._globals['urlencode'] = urllib.parse.quote
        self._globals['urldecode'] = urllib.parse.unquote

    @staticmethod
    def htmlspecialchars(text):
        return cgi.escape(text, True)

    ### Parser and Execution Code ###

    def evaluate(self):
        self._start_time = time.time()

        self._output = io.StringIO()
        segments = self._parse_segments(self._contents)
        self._pycode = self._generate_python(segments)
        output = self._execute_python()

        nerve.log("pyhtml executed in %.4f seconds" % (time.time() - self._start_time,))
        self._start_time = 0
        return output

    def pyhtmleval(self, code):
        segments = self._parse_segments(code)
        pycode = self._generate_python(segments)
        exec(pycode, self._globals)

    def _read_contents(self, filename):
        with open(filename, 'r') as f:
            contents = f.read()
        return contents

    def _parse_segments(self, contents):
        segments = [ ]
        while contents != '':
            first = contents.partition('<%')
            second = first[2].partition('%>')

            segments.append({ 'type' : 'raw', 'data' : first[0] if len(first[0]) > 0 and first[0][-1] == '\n' else first[0].rstrip(' \t') })

            if second[0]:
                if second[0].startswith('%include'):
                    include = self._read_contents(second[0].replace('%include', '').strip())
                    segments.extend(self._parse_segments(include))
                elif second[0][0] == '=':
                    segments.append({ 'type' : 'eval', 'data' : second[0][1:] })
                else:
                    segments.append({ 'type' : 'exec', 'data' : second[0] })

            if len(second[2]) > 0 and second[2][0] == '\n':
                contents = second[2][1:]
            else:
                contents = second[2]
        return segments

    def _generate_python(self, segments):
        base = len(self._segments)
        self._segments += segments

        lines = [ ]
        for i, seg in enumerate(segments):
            i += base
            if seg['type'] == 'raw':
                lines.append("py._output.write(py._segments[%d]['data'])" % (i,))
            elif seg['type'] == 'eval':
                lines.append("py._output.write(str(eval(py._segments[%d]['data'])))" % (i,))
            elif seg['type'] == 'exec':
                sublines = seg['data'].split('\n')
                lines.extend(sublines)

        lines = self._fix_indentation(lines)
        return '\n'.join(lines)

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

    def _execute_python(self):

        old_stdout = sys.stdout

        try:
            sys.stdout = self._output
            exec(self._pycode, self._globals)

        except Exception as e:
            print('\n<b>Eval Error:</b>\n<pre>\n%s</pre><br />\n' % (traceback.format_exc(),))
            print('<br /><pre>' + self.htmlspecialchars('\n'.join([ str(num + 1) + ':  ' + line for num,line in enumerate(self._pycode.splitlines()) ])) + '</pre>')

        finally:
            sys.stdout = old_stdout

        return self._output.getvalue()


