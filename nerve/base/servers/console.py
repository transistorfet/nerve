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

    @classmethod
    def get_config_info(cls):
        config_info = super().get_config_info()
        config_info.add_setting('controllers', "Controllers", default={
            '__default__' : {
                '__type__' : 'base/QueryController'
            }
        })
        return config_info

    def send(self, text):
        print(text)

    def run(self):
        # TODO you should grab the stdin and stdout at the start so that it doesn't interfer with webpages that override 'print'

        with nerve.users.login('admin', 'admin'):
            # TODO i don't like how this happens...  you shouldn't have to create a request
            controller = self.make_controller(nerve.Request(self, None, 'QUERY', "/", { }))
            if hasattr(controller, 'tab_complete'):
                readline.set_completer(controller.tab_complete)
                readline.parse_and_bind("tab: complete")

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
                        request = nerve.Request(self, None, 'QUERY', "/", { 'queries[]' : [ line ] }, headers=dict(accept='text/plain, text/html, application/json'))
                        controller.handle_request(request)
                        mimetype = controller.get_mimetype()
                        output = controller.get_output()

                        if mimetype == 'application/json':
                            data = json.loads(output.decode('utf-8'))
                            if data and data[0]:
                                print('\n'.join([ str(val) for val in data ]))
                        else:
                            print(output.decode('utf-8'))

                except EOFError:
                    nerve.log("Console received EOF. Exiting...")
                    break

                except:
                    nerve.log(traceback.format_exc())

 
