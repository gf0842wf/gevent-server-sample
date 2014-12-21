# -*- coding: utf-8 -*-

"""multi process and multi greenlet spawn"""

import gevent
import gipc
import random


class PPool(object):
    """process pool + gevent spawn
    : 必须放在入口文件的最开始初调用PPool实例的init函数, 因为子进程会复制主进程空间(包括已有协程)
    from share import ppool; ppool.init()
    import sys; sys.modules.pop("threading", None)
    from gevent import monkey; monkey.patch_all()
    ...
    """
    # TODO: 获得spawn结果---再使用一个主进程读,子进程写的pipe, 主进程通过pipe给子进程传递函数和参数的同时还传递uuid,子进程处理完后,给主进程传递uuid和结果,主进程通过uuid来获得这个结果

    def __init__(self, process_size=1):
        """
        @param process_size: the process pool size
        """
        self.process_size = process_size
        self.pipe_readers = []
        self.pipe_writers = []
        self.processes = []
        
    def init(self):
        for _ in xrange(self.process_size):
            r, w =  gipc.pipe()
            self.pipe_readers.append(r)
            self.pipe_writers.append(w)
            p = gipc.start_process(target=self.process_target, args=(r, ))
            self.processes.append(p)
            #p.join()

    def process_target(self, reader):
        def loop(reader):
            while 1:
                f, args, kwargs = reader.get()
                gevent.spawn(f, *args, **kwargs)
        loop(reader)

    def select_pipe_writer(self,  sn=None):
        if sn is not None:
            return self.pipe_writers[sn]
        return random.choice(self.pipe_writers)

    def spawn(self, f, _sn, *args, **kwargs):
        """
        @param f: func
        @param _sn: 第几个进程伺服该函数, _sn=None为随机选取
        @param args, kwargs: f的参数
        # TODO: spawn返回一个greenlet,通过它来获取结果等状态
        """
        pipe = self.select_pipe_writer(_sn)
        pipe.put([f, args, kwargs])
        
    def close_pipes(self):
        [r.close() for r in self.pipe_readers]
        [w.close() for r in self.pipe_writers]
        
    def __del__(self):
        self.close_pipes()
        
        
if __name__ == "__main__":
    def x(a):
        print a
        while 1:
            pass
        
    ppool = PPool(2)
    ppool.init()
    ppool.spawn(x, 0, "xxxx")
    ppool.spawn(x, 1, "yyyy")

        