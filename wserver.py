# -*- coding: utf-8 -*-

"""WSGI Server Sample"""

import gevent
from gevent import monkey;monkey.patch_all()
from gevent.pywsgi import WSGIServer
import socket

import tornado.web
import tornado.wsgi


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello")


class TestHandler(tornado.web.RequestHandler):
    def get(self):
        gevent.sleep(10)
        self.write("test")


app = tornado.wsgi.WSGIApplication([
    (r"/", MainHandler),
    (r"/test", TestHandler),
])
    
    
class WServerManager(gevent.Greenlet):
    def __init__(self, port, app=None):
        self.port = port
        self.app = app
        gevent.Greenlet.__init__(self)

    def _app(self, environ, start_response):
        start_response('200 OK', [('Content-Type','text/plain')])
        yield "%s\n" % str(socket.getaddrinfo('www.baidu.com', 80))

    def _run(self):
        print("WSGI Server Listen at port {0}".format(self.port))
        server = WSGIServer(('0.0.0.0', self.port), self.app or self._app)
        server.serve_forever()


if __name__ == "__main__":
    ws = WServerManager(7001, app) # 这个是通过协程执行的,所以下面需要一个协程join等待
    ws.start()
    print "....."
    def loop():
        while True:
            gevent.sleep(600)
    lp = gevent.spawn(loop)
    lp.join()