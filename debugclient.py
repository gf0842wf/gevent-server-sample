# -*- coding: utf-8- -*-
 
import socket
import sys
 
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print repr(e)
 
remote_addr = ("127.0.0.1", 7006)
sock.connect(remote_addr)         

f = sock.makefile("r")
while True:
    s = raw_input(">>> ")
    sock.sendall(s+"\n")
    print f.readline()
 
sock.close()
