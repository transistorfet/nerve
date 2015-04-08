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
            for querystr in request.args['queries[]']:
                args = querystr.split()
                tag = args.pop(0)
                result[tag] = nerve.query(self.get_setting('root') + '/' + tag, *args)
        self.write_json(result)


