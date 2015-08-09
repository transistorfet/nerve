#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve


class QueryController (nerve.Controller):
    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('root', "Root Query", default='/devices')
        return config_info

    def do_request(self, request):
        result = None
        querystr = request.get_remaining_segments()

        if querystr != '':
            result = self.execute_query(querystr, **request.args)
        elif 'queries[]' in request.args:
            result = { }
            for i, querystr in enumerate(request.args['queries[]']):
                result[i] = self.execute_query(querystr)
        self.write_json(result)

    def execute_query(self, querystr, **args):
        if querystr[0] != '/' and not querystr.startswith('http:'):
            querystr = self.get_setting('root') + '/' + querystr
        return nerve.query(querystr, **args)

