#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import shlex

class ShellController (nerve.Controller):
    def __init__(self, **config):
        nerve.Controller.__init__(self, **config)
        self.pwd = '/devices'

    def do_request(self, request):
        result = None
        if 'queries[]' in request.args:
            result = [ ]
            for query_string in request.args['queries[]']:
                result.append(self.execute_command(query_string))
        self.write_json(result)

    def execute_command(self, command_line):
        args = shlex.split(command_line)
        command = "cmd_" + args[0]

        if hasattr(self, command):
            func = getattr(self, command)
            result = func(args)
        else:
            result = nerve.query_string(self.pwd + "/" + command_line)
        return result

    def cmd_ls(self, args):
        result = [ ]
        main = nerve.main()

        if len(args) <= 1:
            result = self.print_ls(nerve.get_object(self.pwd))
        else:
            for dirname in args[1:]:
                if dirname[0] == '/':
                    dev = nerve.get_object(dirname)
                else:
                    dev = nerve.get_object(self.pwd + "/" + dirname)

                if not dev:
                    result.append(dirname + "/ not found")
                else:
                    result.append(dirname + "/:")
                    result.extend(self.print_ls(dev))
        return '\n'.join(result)

    def print_ls(self, directory):
        result = [ ]
        for devname in directory.keys():
            dev = getattr(directory, devname)
            if isinstance(dev, nerve.ObjectDirectory):
                result.append("  %s/" % (devname,))
            else:
                result.append("  %s" % (devname,))
        return result

    def cmd_pwd(self, args):
        return str(self.pwd)

    def cmd_cd(self, args):
        if len(args) > 1:
            if args[1][0] == '/':
                newpwd = args[1]
            else:
                newpwd = self.pwd + "/" + args[1]
            if nerve.get_object(newpwd):
                self.pwd = newpwd
        return str(self.pwd)

    def cmd_save(self, args):
        nerve.save_config()

    def cmd_mkdir(self, args):
        pass

    def cmd_rmdir(self, args):
        pass

    def cmd_mv(self, args):
        pass

    def cmd_mkdev(self, args):
        pass


