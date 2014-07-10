# -*- coding: utf-8 -*-

import gevent
from gevent.queue import Queue
from gevent import socket
import struct


class EndPoint(gevent.Greenlet):
    """可以用在服务端/客户端"""
    
    def __init__(self, transport, address):
        self.transport = transport
        self.address = address
        self.header_fmt = struct.Struct('>i')
        self.inbox = Queue()
        self.jobs = []

        gevent.Greenlet.__init__(self)
        
    def __str__(self):
        return "[endpoint:%r]" % (self.address, )

    def put_data(self, data):
        self.inbox.put(data)

    def recv_data(self):
        """如果封包方式不同,需要重载这个函数"""
        while True:
            try:
                length = self.transport.recv(4)
                if not length:
                    self.on_connection_closed()
                    break

                length = self.header_fmt.unpack(length)[0]
                data = self.transport.recv(length)
            except:
                self.on_connection_lost()
                break

            self.on_data(data)

    def send_data(self):
        """如果封包方式不同,需要重载这个函数"""
        while True:
            data = self.inbox.get()
            data_length = len(data)
            fmt = '>i%ds' % data_length
            data_struct = struct.Struct(fmt)
            data = data_struct.pack(data_length, data)
            self.transport.sendall(data)

    def on_data(self, data):
        """called when data received. (stripped the 4 bytes header)"""
        raise NotImplementedError()

    def on_connection_closed(self):
        """called when peer closed the connect"""
        raise NotImplementedError()

    def on_connection_lost(self):
        """called when lost peer"""
        raise NotImplementedError()

    def terminate(self):
        gevent.killall(self.jobs)
        self.transport.close()
        self.kill()

    def _run(self):
        job_recv = gevent.spawn(self.recv_data)
        job_send = gevent.spawn(self.send_data)

        def _exit(glet):
            job_recv.unlink(_exit)
            job_send.unlink(_exit)
            self.terminate()

        job_recv.link(_exit)
        job_send.link(_exit)

        self.jobs.append(job_recv)
        self.jobs.append(job_send)
        

def create_connection(address, timeout=None, **ssl_args):
    """客户端创建连接,返回sock
    :自带有一个 from gevent.socket import create_connection, 不过没有ssl参数
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)
    
    if timeout:
        sock.settimeout(timeout)
    if ssl_args:
        from gevent.ssl import wrap_socket
        sock = wrap_socket(sock, **ssl_args)
        
    host = address[0]
    port = int(address[1]) 
    sock.connect((host, port))
    
    return sock


if __name__ == "__main__":
    import struct
    sock = create_connection(("127.0.0.1", 7000))
    sock.sendall(struct.pack(">I5s", 5, "hello"))
    print repr(sock.recv(10))
