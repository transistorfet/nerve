#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import json
import readline
import traceback

class Console (nerve.Server):
    def __init__(self, **config):
        nerve.Server.__init__(self, **config)
        self.thread = nerve.Task('ConsoleTask', target=self.run)
        self.thread.daemon = True
        self.thread.start()

    @staticmethod
    def get_config_info():
        config_info = nerve.Server.get_config_info()
        config_info.add_setting('controllers', "Controllers", default={
            '__default__' : {
                'type' : 'base/ShellController'
            }
        })
        return config_info

    def send(self, text):
        print (text)

    def run(self):
        controller = self.make_controller(nerve.Request(self, 'QUERY', "/", { }))
        while True:
        #while not self.thread.stopflag.is_set():
            try:
                line = input(">> ")
                if line == 'quit':
                    nerve.quit()
                    break
                elif (line):
                    request = nerve.Request(self, 'QUERY', "/", { 'queries[]' : [ line ] })
                    controller.handle_request(request)
                    if controller.get_mimetype() == 'application/json':
                        output = controller.get_output().decode('utf-8')
                        data = json.loads(output)
                        if data and data[0]:
                            print ('\n'.join([ str(val) for val in data ]))
                    else:
                        print (controller.get_output().decode('utf-8'))

            except EOFError:
                nerve.log("Console received EOF. Exiting...")
                break

            except:
                nerve.log(traceback.format_exc())

 
