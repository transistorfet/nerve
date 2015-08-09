#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import io
import shlex


class ShellController (nerve.Controller):
    def __init__(self, **config):
        super().__init__(**config)
        self.pwd = '/devices'

    def do_request(self, request):
        result = None
        self.set_mimetype('text/plain')
        if 'queries[]' in request.args:
            result = [ ]
            for query_string in request.args['queries[]']:
                self.run_command(query_string)

    def print(self, *objects, sep='', end='\n'):
        self.write_text(sep.join(str(obj) for obj in objects) + end)

    def run_command(self, command_line):
        args = shlex.split(command_line)
        command = "cmd_" + args[0]

        if hasattr(self, command):
            command_func = getattr(self, command)
        else:
            command_func = self.cmd_query
        exec("command_func(args)")

    def tab_complete(self, text, state):
        for name in dir(self):
            if name.startswith('cmd_') and name[4:].startswith(text):
                state -= 1
                if state <= 0:
                    return name[4:]

        """
        if text.startswith('/'):
            (base, sep, partial) = text.rpartition('/')
            obj = nerve.get_object(base if base else '/')
            if not obj:
                return 0
            for name in obj.keys_children() + obj.keys_queries() + obj.keys_attrs():
                if name.startswith(partial):
                    state -= 1
                    if state <= 0:
                        return base + sep + name
        """
        return 0

    def cmd_query(self, args):
        ref = args.pop(0)
        if ref.startswith('/') or ref.startswith('http:'):
            self.print(nerve.query(ref, *args))
        else:
            self.print(nerve.query(self.pwd + "/" + ref, *args))

    def cmd_ls(self, args):
        flags = ''
        dirs = [ ]
        for arg in args[1:]:
            if arg.startswith('-'):
                flags += arg[1:]
            else:
                dirs.append(arg)

        if len(dirs) == 0:
            dirs.append(self.pwd)

        for dirname in dirs:
            directory = nerve.get_object(self.pwd + "/" + dirname if dirname[0] != '/' else dirname)

            if not directory:
                self.print(dirname + "/ not found")
            else:
                self.print(dirname + "/:")

                items = directory.keys_children()
                if 'a' in flags:
                    items += directory.keys_attrs()
                else:
                    items += directory.keys_queries()

                for itemname in sorted(items):
                    item = getattr(directory, itemname)
                    if isinstance(item, nerve.ObjectNode):
                        self.print("  %s/" % (itemname,))
                    else:
                        self.print("  %s" % (itemname,))

    def cmd_pwd(self, args):
        self.print(self.pwd)

    def cmd_cd(self, args):
        if len(args) > 1:
            if args[1][0] == '/':
                newpwd = args[1]
            else:
                newpwd = self.pwd + "/" + args[1]
            if nerve.get_object(newpwd):
                self.pwd = newpwd
        self.print(self.pwd)

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

    def cmd_lastlog(self, args):
        for line in nerve.logs.buffer():
            self.print(line.strip())

    def cmd_logs(self, args):
        if len(args) < 2:
            self.print("Usage: logs [on|off]")
            return

        cmd = args[1].lower()
        if cmd == 'on':
            nerve.logs.redirect(nerve.logs.stdout)
        elif cmd == 'off':
            nerve.logs.redirect(None)

    def cmd_owner(self, args):
        self.print(str(nerve.main().users.thread_owner()))

    def cmd_thread_count(self, args):
        self.print(str(nerve.main().users.thread_count()))

