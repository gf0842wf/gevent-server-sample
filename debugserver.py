# -*- coding: utf-8 -*-

"""部署服务时,debug服务用来交互式修改主程序运行时数据,类似twisted的ssh服务"""

# prefix = ">>> "
# exec "from time import sleep"
# exec "sleep(3)"
# exec "d={'a':4}"
# exec "d['a'] = 5"
# exec "print d"

import socket
 
fd_map = {} # fd到socket的映射, 记住服务器socket和连接进来的客户端socket,可以向指定连接通信
 
# 建立socket对象
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fd = sock.fileno()
    fd_map[fd] = sock
except socket.error as e:
    print repr(e)
 
# 设置socket选项 这里设置SO_REUSEADDR含义:当socket意外关闭,马上释放占有的端口
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
# 绑定到某个端口
host_addr = ("0.0.0.0", 7006)
sock.bind(host_addr)
 
sock.listen(5)
 
while True:
    # 接受连接 accept返回连接的socket对象和addr
    conn, addr = sock.accept()
    fd_map[fd] = conn
    f = conn.makefile()
    while True:
        cmd = f.readline().rstrip("\n")
        try:
            result = eval(cmd)
        except:
            result = "" # globals()
#             exec cmd
        print repr(cmd)
        conn.sendall("%s\nab\n" % result)
 
# 关闭socket
sock.close()