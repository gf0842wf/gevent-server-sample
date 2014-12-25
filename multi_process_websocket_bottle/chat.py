# -*- coding: utf-8 -*-

"""Multi Process WSGI And WebSocket Server Sample"""

# 注意修改: .tpl文件里面的ws的ip和端口

from gevent import monkey; monkey.patch_all()# monkey.patch_os()
from gevent.pywsgi import WSGIServer
from multiprocessing import Process
import gevent

from geventwebsocket.handler import WebSocketHandler

from bottle import Bottle, template, run
#from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket

app = Bottle()
users = set()

@app.route('/', method='GET')
def index():
    return template('index')

@app.route('/websocket', apply=[websocket], method='GET')
def chat(ws):
    users.add(ws)
    while True:
        msg = ws.receive()
        if msg is not None:
            for u in users:
                u.send(msg)
        else: break
    users.remove(ws)

server = WSGIServer(('0.0.0.0', 6000), app, handler_class=WebSocketHandler, backlog=100000, log=None)
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