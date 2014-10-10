# -*- coding: utf-8- -*-
 
import socket
import sys, os

ARGS = filter(lambda arg: isinstance(arg, list) and len(arg)==2, 
              [arg.lstrip("-").split("=") for arg in sys.argv[1:]])
ARGS = dict(ARGS)

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print repr(e)
 
remote_addr = (ARGS["host"], int(ARGS["port"]))
sock.connect(remote_addr)         

f = sock.makefile("r")
while True:
    s = raw_input(">>> ")
    sock.sendall(s+"\n")
    print sock.recv(4196).rstrip("\n") # 简单接收了,没做分包粘包处理
 
sock.close()

# python debugclient.py --host=127.0.0.1 --port=8106