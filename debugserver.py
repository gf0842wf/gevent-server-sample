# -*- coding: utf-8 -*-

"""部署服务时,debug服务用来交互式修改主程序运行时数据,用python进行交互操作"""
"""危险声明: 一旦掌握此权限,可以对程序进行任何查看和修改!!!最好是通过ssh跳转来操作(debugserver端口不对外开放,在服务器执行debugclient来连接)"""

# 客户端交换命令如下
# 执行语句---需要加上exec
# exec "from time import sleep"
# exec "sleep(3)"
# exec "d={'a':4}"
# exec "d['a'] = 5"

# 执行表达式---直接运行表达式
# addr

# 执行print---直接print 表达式--这个可以不用,直接用执行表达式即可打印出来
# print addr <==> addr


import socket
import threading
import logging
 
def start_server(host_addr):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        logging.error(repr(e))
     
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
     
    sock.bind(host_addr)
    logging.info("debugserver start @ %s" % str(host_addr))
     
    sock.listen(5)
    
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=connection_handler, args=(conn, addr)).start()
    
def connection_handler(conn, addr):
    logging.info("client %s connected" % str(addr))
    f = conn.makefile()
    while True:
        try:
            cmd = f.readline().rstrip("\n")
        except Exception as e:
            logging.info("client %s closed | %s" % (str(addr), e))
            break
        if cmd.startswith("exec"):
            try:
                exec cmd
                result = ""
            except Exception as e:
                result = "%s: %s" % (e.__class__, str(e))
        else:
            if cmd.startswith("print"):
                cmd = cmd[5:].lstrip()
            try:
                result = eval(cmd)
            except Exception as e:
                result = "%s: %s" % (e.__class__, str(e))
        conn.sendall("%s\n" % str(result))
    conn.close()
        

if __name__ == "__main__":
    start_server(("0.0.0.0", 8106))
