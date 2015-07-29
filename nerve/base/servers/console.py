#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import sys
import time
import json
import readline
import traceback

class Console (nerve.Server):
    def __init__(self, **config):
        super().__init__(**config)
        self.thread = nerve.Task('ConsoleTask', target=self.run)
        self.thread.daemon = True
        self.thread.start()

    @staticmethod
    def get_config_info():
        config_info = nerve.Server.get_config_info()
        config_info.add_setting('controllers', "Controllers", default={
            '__default__' : {
                '__type__' : 'base/QueryController'
            }
        })
        return config_info

    def send(self, text):
        print(text)

    def run(self):
        # TODO this is to fix a race condition where the parent server object, /servers/default_shell, hasn't been created yet, and
        # make_controller fails as a result.  Maybe there should be a secondary 'start threads' phase after the config objects have been
        # created
        time.sleep(3)

        controller = self.make_controller(nerve.Request(self, None, 'QUERY', "/", { }))
        while True:
        #while not self.thread.stopflag.is_set():
            try:
                #print(">> ", end='', flush=True)
                #line = sys.stdin.readline().strip()
                line = input(">> ")
                if line == 'quit':
                    nerve.quit()
                    break
                elif line:
                    request = nerve.Request(self, None, 'QUERY', "/", { 'queries[]' : [ line ] })
                    controller.handle_request(request)
                    if controller.get_mimetype() == 'application/json':
                        output = controller.get_output().decode('utf-8')
                        data = json.loads(output)
                        if data and data[0]:
                            print('\n'.join([ str(val) for val in data ]))
                    else:
                        print(controller.get_output().decode('utf-8'))

            except EOFError:
                nerve.log("Console received EOF. Exiting...")
                break

            except:
                nerve.log(traceback.format_exc())

 
