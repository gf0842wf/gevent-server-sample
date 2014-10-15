# -*- coding: utf-8 -*-

"""gevent websocket server"""

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource


class EchoApplication(WebSocketApplication):
    def on_open(self):
        print "Connection opened"

    def on_message(self, message):
        self.ws.send(message)

    def on_close(self, reason):
        print reason


if __name__ == "__main__":
    wss = WebSocketServer(('', 7007),Resource({'/': EchoApplication}))
    wss.serve_forever()