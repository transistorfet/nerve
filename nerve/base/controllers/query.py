#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve


class QueryController (nerve.Controller):
    def do_request(self, request):
	result = None
	querystr = request.remaining_segments().replace('/', '.')
	if querystr != '':
	    result = nerve.query(querystr, **request.args)
	elif 'queries[]' in request.args:
	    result = { }
	    for querystr in request.args['queries[]']:
		args = querystr.split()
		tag = args.pop(0)
		result[tag] = nerve.query(tag, *args)
	self.write_json(result)

    """
    def do_query(self, kwargs):
	print "Vars: " + repr(kwargs)
	try:
	    if 'tag' in kwargs:
		result = nerve.query_string(kwargs['tag'][0])
	    elif 'ref' in kwargs:
		ref = kwargs['ref'][0]
		del kwargs['ref'][0]
		# TODO also convert at least GET vars from %20 chars to ascii...
		for key in kwargs.keys():
		    if len(kwargs[key]) <= 1:
			kwargs[key] = kwargs[key][0]
		result = nerve.query(ref, **kwargs)
	except:
	    result = { 'error' : "something went wrong" }

	self.send_json_headers()
	self.wfile.write(json.dumps(result))
	return
    """


