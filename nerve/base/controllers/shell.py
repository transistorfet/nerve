#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import shlex

class ShellController (nerve.Controller):
    def do_request(self, request):
        result = None
        if 'queries[]' in request.args:
            result = [ ]
            for query_string in request.args['queries[]']:
                result.append(self.execute_command(query_string))
        self.write_json(result)

    def execute_command(self, command_line):
        result = [ ]
        main = nerve.main()
        args = shlex.split(command_line.encode('utf-8'))

        if args[0] == 'ls':
            if len(args) < 2:
                result = self.print_ls(main.devices)
            else:
                for pwd in args[1:]:
                    dev = main.devices.get_object(pwd)
                    if not dev:
                        result.append(pwd + "/ not found")
                    else:
                        result.append(pwd + "/:")
                        result.extend(self.print_ls(dev))
        else:
            result = nerve.query_string(command_line)
        return result

    def print_ls(self, table):
        result = [ ]
        for devname in table.keys():
            dev = getattr(table, devname)
            if isinstance(dev, nerve.ConfigObjectTable):
                result.append("%s/" % (devname,))
            else:
                result.append("%s" % (devname,))
        return result


