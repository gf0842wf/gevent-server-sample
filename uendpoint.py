# -*- coding: utf-8 -*-

"""UDP Server Sample"""

import gevent
from gevent.queue import Queue
from gevent import socket


class EndPoint(gevent.Greenlet):
    
    def __init__(self, svr, address):
        self.svr = svr
        self.address = address
        self.inbox = Queue()
        self.jobs = []

        gevent.Greenlet.__init__(self)

    def __str__(self):
        return "[endpoint:%r]" % (self.address, )
        
    def put_data(self, data):
        self.inbox.put(data)
        
    def on_data(self, data):
        """called when data received. (stripped the 4 bytes header)"""
        raise NotImplementedError()

    def send_data(self):
        """如果封包方式不同,需要重载这个函数"""
        while True:
            data = self.inbox.get()
            self.svr.sendto(data, self.address)
        
    def handle(self, datagram):
        """如果封包方式不同,需要重载这个函数"""
        self.on_data(datagram)

    def terminate(self):
        gevent.killall(self.jobs)
        self.kill()
        
    def _run(self):
        job_send = gevent.spawn(self.send_data)
        self.jobs.append(job_send)
        
        def _exit(glet):
            job_send.unlink(_exit)
            self.terminate()
            
        job_send.link(_exit)
        
        
def create_socket(timeout=None, **ssl_args):
    """客户端创建,返回sock
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    if timeout:
        sock.settimeout(timeout)
    if ssl_args:
        from gevent.ssl import wrap_socket
        sock = wrap_socket(sock, **ssl_args)
    
    return sock


if __name__ == "__main__":
    sock = create_socket()
    sock.sendto("hello", ("127.0.0.1", 7002))
    print sock.recvfrom(512)