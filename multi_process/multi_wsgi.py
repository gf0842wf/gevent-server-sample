# -*- coding: utf-8 -*-

"""Multi Process WSGI Server Sample"""

from gevent import monkey; monkey.patch_os()
from gevent.pywsgi import WSGIServer
from multiprocessing import Process
import gevent

def app(environ, start_response):
    start_response('200 OK', [('Content-Type','text/plain')])
    yield "hello\n"

server = WSGIServer(('0.0.0.0', 6000), app, backlog=100000, log=None)
server.init_socket()

def serve_forever():
    server.start_accepting()
    server._stop_event.wait()
    gevent.wait()

process_count = 2
processes = []
for i in range(process_count):
    p = Process(target=serve_forever, args=tuple())
    p.start()
    processes.append(p)

try:
    print "main process .."
    serve_forever() # 主进程也跑一个
    for p in processes:
        p.join()
except KeyboardInterrupt:
    print "bye"
    
