# -*- coding: utf-8 -*-

"""UDP Server Sample"""

import gevent
from gevent.server import DatagramServer


class Bot(object):
    
    def __init__(self, svr, address):
        self.svr = svr
        self.address = address
        
    def __str__(self):
        return "[bot:%r]" % (self.address, )
        
    def handle(self, datagram):
        print '%s: got %r ' % (self, datagram)
        self.svr.sendto(datagram, self.address)
    

class UDPServer(DatagramServer):
    clients = {}
    
    def handle(self, datagram, address):
        """有datagram到来时会调用handle
        :可以根据address/uid来建立endpoint(这里是Bot对象)
        """
        # self.socket.sendto(datagram, address)
        # self.sendto(datagram, address)
        client = self.clients.get(address)
        if not client:
            client = self.clients.setdefault(address, Bot(self, address))
        client.handle(datagram)


class UDPManager(gevent.Greenlet):
    
    def __init__(self, port):
        self.port = port
        gevent.Greenlet.__init__(self)

    def _run(self):
        print("UDP Server at port {0}".format(self.port))
        server = UDPServer(('0.0.0.0', self.port))
        server.serve_forever()


if __name__ == '__main__':
    us = UDPManager(7002)
    us.start()
    gevent.wait()
    