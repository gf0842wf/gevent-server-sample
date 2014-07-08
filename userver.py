# -*- coding: utf-8 -*-

"""UDP Server Sample"""

import gevent
from gevent.server import DatagramServer


class UDPServer(DatagramServer):

    def handle(self, datagram, address):
        """有datagram到来时会调用handle"""
        print('%s: got %r' % (address[0], datagram))
        self.socket.sendto(datagram, address)
        # self.sendto(datagram, address)

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
    