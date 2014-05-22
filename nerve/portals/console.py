#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import traceback

class Console (nerve.Portal, nerve.Task):
    def __init__(self):
	nerve.Task.__init__(self, 'ConsoleTask')
	self.daemon = True
	self.start()

    def send(self, text):
	print text

    def run(self):
        while 1:
	    try:
		line = raw_input(">> ")
		if line == 'quit':
		    break
		elif (line):
		    msg = nerve.Message(line, self, self)
		    nerve.dispatch(msg)

	    except EOFError:
		nerve.log("Console received EOF. Exiting...")
		break

	    except:
		nerve.log(traceback.format_exc())

 
