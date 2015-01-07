#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve


class PyExecController (nerve.Controller):
    def do_request(self, request):
	result = None
	if 'queries[]' in request.args:
	    result = [ ]
	    for querystr in request.args['queries[]']:
		result.append(eval(querystr, nerve.main().devices))
	self.write_json(result)


