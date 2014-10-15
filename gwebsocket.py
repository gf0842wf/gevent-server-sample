# -*- coding: utf-8 -*-

"""gevent websocket server"""

# https://github.com/jgelens/gevent-websocket

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource


class EchoApplication(WebSocketApplication):
    def on_open(self):
        print "Connection opened"

    def on_message(self, message):
        self.ws.send(message)

    def on_close(self, reason):
        print reason


if __name__ == "__main__":
    wss = WebSocketServer(('', 8201),Resource({'/chat': EchoApplication}))
    wss.serve_forever()