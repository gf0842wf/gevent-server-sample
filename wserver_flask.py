# -*- coding: utf-8 -*-

"""WSGI Server Sample"""

import gevent
from gevent import socket
from gevent.pywsgi import WSGIServer
from gmysql import Pool
from flask import Flask, g

app = Flask(__name__)

app.config.update(dict(
                       DB = ('localhost', 'root', '112358', 'test')
                       )
                  )

pool = Pool(app.config["DB"], 6)


@app.route("/")
def hello():
    rows = pool.fetchall("select * from book")
    print rows
    return str(rows)

@app.route("/sleep")
def sleep():
    gevent.sleep(5)
    return "awake..."
    
    
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