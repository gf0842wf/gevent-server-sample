# -*- coding: utf-8 -*-

# https://github.com/gf0842wf/websocket-client

from gevent import monkey; monkey.patch_all()
from gevent.pool import Pool
import gevent
import websocket
import ujson

# websocket.enableTrace(True)
    
def test_NOP(ws):
    ws.send(ujson.dumps({"type":"NOP"}))
    result = ws.recv()
    print result
    gevent.sleep(3600)
    ws.close()
    
if __name__ == "__main__":
#     pool = Pool(2000)
#     pool.map(test_NOP, (websocket.create_connection("ws://121.40.104.140:8201/chat") for _ in xrange(2000))])
    for i in xrange(2000):
        gevent.spawn(test_NOP, websocket.create_connection("ws://121.40.104.140:8201/chat"))
        
    gevent.wait()
