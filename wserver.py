# -*- coding: utf-8 -*-

"""WSGI Server Sample"""

import gevent
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer

import tornado.web
import tornado.wsgi

from gmysql import Pool


class MainHandler(tornado.web.RequestHandler):
    
    def get(self):
        rows = self.application.pool.fetchall("select * from book")
        print rows
        self.write("{0}".format(rows))


class TestHandler(tornado.web.RequestHandler):
    
    def get(self):
        gevent.sleep(5)
        self.write("Test")


app = tornado.wsgi.WSGIApplication([
    (r"/", MainHandler),
    (r"/test", TestHandler),
])
args = ('localhost', 'root', '112358', 'test')
pool = Pool(args, 20)
app.pool = pool
    
    
class WServerManager(gevent.Greenlet):
    
    def __init__(self, port, app=None):
        self.port = port
        self.app = app
        gevent.Greenlet.__init__(self)

    def _app(self, environ, start_response):
        start_response('200 OK', [('Content-Type','text/plain')])
        yield "{0}\n".format(socket.getaddrinfo('www.baidu.com', 80))

    def _run(self):
        print("WSGI Server Listen at port {0}".format(self.port))
        server = WSGIServer(('0.0.0.0', self.port), self.app or self._app)
        server.serve_forever()


if __name__ == "__main__":
    ws = WServerManager(7001, app)
    ws.start()
    gevent.wait()
    
