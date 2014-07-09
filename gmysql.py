# -*- coding: utf-8 -*-

"""mysql db connection and pool for gevent
dependent packages: gevent, ultramysql
support reconnect
default charset set to utf8
default autocommit=1 (Transction is not recommended)
default cursorclass=DictCursor
"""
import gevent
from gevent import monkey; monkey.patch_socket()
from gevent.queue import Queue
from gevent.event import AsyncResult
import time
import sys
import umysql
import socket
import traceback

def IDGenerator():
    i = 0
    wall = 1 << 31
    while True:
        i += 1
        if i > wall:
            i = 1
        yield i


class Connection(object):
    reconnect_delay = 8 #重连等待时间
    
    def __init__(self, host, user, passwd, db, port=3306, autocommit=True, charset='utf8'):
        self.args = (host, port, user, passwd, db, autocommit, charset)
        self.conn = umysql.Connection()
        self.conn.connect(*self.args)

    def reconnect(self, delay):
        while True:
            self.conn.close()
            self.conn = umysql.Connection()
            try:
                print 'Trying reconnect..'
                self.conn.connect (*self.args)
                print 'Reconneced.'
                break
            except:
                print sys.exc_info()
            gevent.sleep(delay)
    
    def query(self, sql, args):
        if args:
            assert isinstance(args, (tuple, list))
        try:
            return self.conn.query(sql, args)
        except socket.error:
            print '[Sending Query]:', sql
            print sys.exc_info()
            self.reconnect(self.reconnect_delay)
            return self.conn.query(sql, args)
        except:
            if not self.conn.is_connected():
                print '[Sending Query]:', sql
                print sys.exc_info()
                self.reconnect(self.reconnect_delay)
                return self.conn.query(sql, args)
            else:
                raise


class PoolError(Exception):
    pass


class Pool(object):
    """[连接池] 每个连接使用一个gevent队列的连接池
    - 队列格式: (sql, args, )
    """
    def __init__(self, args, n):
        assert n > 0, n
        self.conns = []
        self.queues = []
        self.tasks = []

        for _ in xrange(n):
            c = Connection(*args)
            self.conns.append(c)
            q = Queue()
            self.queues.append(q)
            g = gevent.spawn(self.loop, c, q)
            self.tasks.append(g)
    
        assert len(self.conns) == n
    
    def get_result_rows(self, rs, curclass):
        if not curclass or curclass == 'dict':
            fields = [row[0] for row in rs.fields]
            return [dict(zip(fields, row)) for row in rs.rows]
        else:
            return rs.rows
    
    def loop(self, conn, q):
        """
        - 队列格式: (sql, args, op, curclass, result),
        - op是操作类型, 0是execute, 1是fetchone, 2是fetchall, 3是获得结果字段名列表
        - curclass是结果集类型, 默认是dict(字典), 也可以是list(列表).
        - result是gevent的AsyncResult对象, result为空则非阻塞
        """
        while 1:
            sql, args, op, curclass, result = q.peek()
            try:
                rs = conn.query(sql, args)
                if result:
                    if op == 0:
                        result.set(rs[1] or rs[0])
                    elif op == 1:
                        rows = self.get_result_rows(rs, curclass)
                        row = rows and rows[0] or None
                        result.set(row)
                    elif op == 2:
                        rows = self.get_result_rows(rs, curclass)
                        result.set(rows)
                    elif op == 3:
                        fields = [row[0] for row in rs.fields]
                        result.set(fields)
                    else:
                        raise PoolError("Query Op is wrong. %s" % op)
            except:
                print '[LastQuery]:', sql, args
                if result:
                    result.set_exception(sys.exc_info()[1])
                else:
                    print traceback.format_exc()
            finally:
                q.next()

    def selectq(self, qid=-1):
        """选择第几个队列, 默认返回长度最小的队列"""
        if qid >= 0:
            return self.queues[qid%len(self.queues)]
#         minq = self.queues[0]
#         for q in self.queues:
#             if minq.qsize() > q.qsize():
#                 minq = q
        minq = min(self.queues, key=lambda qs:qs.qsize())
        return minq

    def query(self, sql, args=[], op=0, qid=-1, curclass=None, block=True):
        if not isinstance(qid, (int, long)):
            qid = -1
        q = self.selectq(qid)
        if block:
            result = AsyncResult()
            q.put((sql, args, op, curclass, result))
            return result.get()
        else:
            q.put((sql, args, op, curclass, None))

    def execute(self, sql, args=[], qid=-1, curclass=None, block=True):
        return self.query(sql, args, 0, qid, curclass, block)
    
    def fetchone(self, sql, args=[], qid=-1, curclass=None, block=True):
        return self.query(sql, args, 1, qid, curclass, block)

    def fetchall(self, sql, args=[], qid=-1, curclass=None, block=True):
        return self.query(sql, args, 2, qid, curclass, block)

    def get_fields(self, tbname):
        return self.query("select * from %s limit 0"%tbname, [], 3, qid=-1, curclass=None, block=True)

    
if __name__ == '__main__':
    args = ('localhost', 'root', '112358', 'test')
    pool = Pool(args, 20)
    print pool.fetchall("select * from book")
    
    # 像 execute 如果不关心执行结果,可以异步执行,不过记得join/wait等待
    pool.execute("insert into book set name='abc', author='fk'")
    gevent.wait()