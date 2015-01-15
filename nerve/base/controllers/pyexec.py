#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve


class PyExecController (nerve.Controller):
    def do_request(self, request):
	result = None
	if 'queries[]' in request.args:
	    result = [ ]
	    global_dict = nerve.main().devices.objects.copy()
	    global_dict['nerve'] = nerve
	    for querystr in request.args['queries[]']:
		result.append(eval(querystr, global_dict))
	self.write_json(result)


