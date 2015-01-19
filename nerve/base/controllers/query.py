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


