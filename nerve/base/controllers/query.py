#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import traceback


class QueryController (nerve.Controller):
    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('root', "Root Query", default='/devices')
        return config_info

    def do_request(self, request):
        result = None
        querystr = request.get_slug()

        if querystr != '':
            result = self.execute_query(querystr, **request.args)
        elif 'requests[]' in request.args:
            result = [ ]
            for querystr in request.args['requests[]']:
                try:
                    result.append(self.execute_query(querystr))
                except:
                    nerve.log(traceback.format_exc(), logtype='error')
                    result.append('error')
        self.load_json_view(result)

    def execute_query(self, querystr, **args):
        if querystr[0] != '/' and not querystr.startswith('http:'):
            querystr = self.get_setting('root') + '/' + querystr
        return nerve.query(querystr, **args)

