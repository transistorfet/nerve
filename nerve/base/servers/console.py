#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import readline
import traceback

class Console (nerve.Server, nerve.Task):
    def __init__(self, **config):
	nerve.Server.__init__(self, **config)
	nerve.Task.__init__(self, 'ConsoleTask')
	#self.daemon = True
	self.start()

    @staticmethod
    def get_defaults():
	defaults = nerve.Server.get_defaults()
	defaults['controllers']['__default__'] = {
	    'type' : 'base/QueryController'
	}
	return defaults

    def send(self, text):
	print text

    def run(self):
        #while True:
        while not self.stopflag.is_set():
	    try:
		line = raw_input(">> ")
		if line == 'quit':
		    break
		elif (line):
		    #result = nerve.query_string(line)
		    #print repr(result)
		    args = line.split()
		    request = nerve.Request(self, 'QUERY', args[0], { })
		    controller = self.find_controller(request)
		    controller.handle_request(request)
		    print controller.get_output()

	    except EOFError:
		nerve.log("Console received EOF. Exiting...")
		break

	    except:
		nerve.log(traceback.format_exc())

 
