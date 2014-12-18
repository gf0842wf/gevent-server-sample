# -*- coding: utf-8 -*-

"""WSGI Server Sample"""

import gevent
from gevent import socket
from gevent.pywsgi import WSGIServer

import tornado.web
import tornado.wsgi


class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        self.write("hello")


class SleepHandler(tornado.web.RequestHandler):
    
    def get(self):
        gevent.sleep(5)
        self.write("Test")


app = tornado.wsgi.WSGIApplication([
    (r"/", MainHandler),
    (r"/sleep", SleepHandler),
])
    
    
class WServerManager(gevent.Greenlet):
    
    def __init__(self, port, app=None):
        self.port = port
        self.app = app
        gevent.Greenlet.__init__(self)

    def _app(self, environ, start_response):
        start_response('200 OK', [('Content-Type','text/plain')])
        yield "hello\n"

    def _run(self):
        print "WSGI Server Listen at port %s" % self.port
        server = WSGIServer(('0.0.0.0', self.port), self.app or self._app)
        server.serve_forever()


if __name__ == "__main__":
    ws = WServerManager(6000, app)
    ws.start()
    
    gevent.wait()
    
