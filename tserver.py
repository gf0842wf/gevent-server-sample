# -*- coding: utf-8 -*-

"""TCP Server Sample"""

import gevent
from gevent.server import StreamServer
from tendpoint import EndPoint


class Bot(EndPoint):
    
    def on_connection_closed(self):
        print("Bot {0} closed the connecton".format(id(self)))

    def on_connection_lost(self):
        print("Bot {0} lost".format(id(self)))

    def on_data(self, data):
        print '%s: got %r ' % (self, data)
        self.put_data(data)


class TCPManager(gevent.Greenlet):
    
    def __init__(self, port):
        self.port = port
        gevent.Greenlet.__init__(self)

    def _connection_handler(self, trans, address):
        # 这里 trans 是socket
        print("New Connection From {0}".format(address))
        bot = Bot(trans, address)
        bot.start()

    def _run(self):
        print("TCP server Listen at port {0}".format(self.port))
        server = StreamServer(('0.0.0.0', self.port), self._connection_handler)
        server.serve_forever()


if __name__ == "__main__":
    ob = TCPManager(7000) # 这个是通过协程执行的,所以下面需要wait等待
    ob.start()
    gevent.wait()
    