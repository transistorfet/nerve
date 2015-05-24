#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve


class QueryController (nerve.Controller):
    @staticmethod
    def get_config_info():
        config_info = nerve.Controller.get_config_info()
        config_info.add_setting('root', "Root Query", default='/devices')
        return config_info

    def do_request(self, request):
        result = None
        querystr = request.remaining_segments()
        if querystr != '':
            result = nerve.query(self.get_setting('root') + '/' + querystr, **request.args)
        elif 'queries[]' in request.args:
            result = { }
            for i, querystr in enumerate(request.args['queries[]']):
                result[i] = nerve.query(self.get_setting('root') + '/' + querystr)
        self.write_json(result)


