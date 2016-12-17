#!/usr/bin/python3

#nerve_install = '/home/trans/projects/nerve-develop'
#nerve_config = '/home/trans/projects/nerve-develop/config/wsgi'
nerve_install = '/home/trans/sites/nerve.jabberwocky.ca/nerve'
nerve_config = '/home/trans/sites/nerve.jabberwocky.ca/nerve/config/wsgi'


import sys

sys.path.insert(0, nerve_install)

import nerve
import nerve.http.servers.wsgi

nerve.files.add_config_path(nerve_config)
nerve.logs.redirect(None)
nerve.logs.log_to_file(True)
nerve.log("starting nerve wsgi gateway", logtype='info')

nerve.get_root()
#nerve.Task.start_all()

#application = nerve.http.servers.wsgi.WSGIHandler(parent='/servers/default')
application = nerve.get_object('/servers/wsgi')

"""
def application(environ, start_response):
    content = b"Disabled"
    headers = [ ('Content-Type', 'text/html'), ('Content-Length', str(len(content))) ]

    start_response('200 OK', headers)
    yield content
"""

