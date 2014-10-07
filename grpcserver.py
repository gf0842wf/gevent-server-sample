# -*- coding: utf-8 -*-

"""gevent rpc server sample"""

# https://github.com/gf0842wf/mprpc
# pip install git+https://github.com/gf0842wf/mprpc.git

from mprpc import RPCServer


class TaskServer(RPCServer):
    
    def echo(self, x):
        return x
    
"""rpc client
from mprpc import RPCClient
rpcclient = RPCClient("127.0.0.1", 7005)
rpcclient.echo("abcd")
"""

if __name__ == "__main__":
    from gevent.server import StreamServer
    server = StreamServer(("0.0.0.0", 7005), TaskServer)
    server.serve_forever()