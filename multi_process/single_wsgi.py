# -*- coding: utf-8 -*-

"""Single Process WSGI Server Sample"""

from gevent.pywsgi import WSGIServer
import gevent

def _app(environ, start_response):
    start_response('200 OK', [('Content-Type','text/plain')])
    yield "hello\n"

server = WSGIServer(('0.0.0.0', 6000), _app, backlog=100000, log=None)

if __name__ == "__main__":
    server.serve_forever()
    
    gevent.wait()
    
