# -*- coding: utf-8 -*-

"""multi process and multi greenlet spawn"""

from gevent.queue import Queue
from functools import partial
import gevent
import gipc
import random

def id_generator():
    i = 0
    wall = 1 << 31
    while True:
        i += 1
        if i > wall:
            i = 1
        yield i
        

class PPool(object):
    """process pool + gevent spawn
    : 1.必须放在入口文件的最开始处调用PPool实例的init函数, 因为子进程会复制主进程空间(包括已有协程)
    : 2.如果需要子进程也包含某些模块/全局变量,可以在模块/全局变量导入后再调用init函数,原则是不能复制过多主进程空间
    Example:
    from share import ppool; ppool.init()
    import sys; sys.modules.pop("threading", None)
    from gevent import monkey; monkey.patch_all()
    import gevent
    
    def foo(a):
        print a
        
    ppool.spawn_unblock(foo, "abc")
    
    gevent.wait()
    """

    def __init__(self, process_size=1):
        """
        @param process_size: the process pool size
        """
        self.id_generator = id_generator()
        self.process_size = process_size
        self.parent_pipe_ends = []         # 存放process_size个双向pipe的父进程端
        self.child_pipe_ends = []          # 存放process_size个双向pipe的子进程端
        self.processes = []                # 存放process_size个子进程
        self.results = {}                  # 在阻塞模式下存放结果, {task_id:Queue(maxsize=1)}
        self.loop_get_result_glets = []    # 存放 loop_get_result 产生的process_size个greenlet
        
    def init(self):
        for _ in xrange(self.process_size):
            child_pipe_end, parent_pipe_end =  gipc.pipe(duplex=True)
            self.child_pipe_ends.append(child_pipe_end)
            self.parent_pipe_ends.append(parent_pipe_end)
            p = gipc.start_process(target=self.process_target, args=(child_pipe_end, ), daemon=True)
            self.processes.append(p)
            #p.join()
            
            self.loop_get_result()
            
    def loop_get_result(self):
        """循环读取子进程返回结果"""
        def loop(p):
            while 1:
                k, v = p.get()
                self.results[k] = self.results[k].put_nowait(v)
                
        for p in self.parent_pipe_ends:
            g = gevent.spawn(loop, p)
            self.loop_get_result_glets.append(g)
        
    def process_target(self, child_pipe_end):
        """子进程空间"""
        def callback(g, task_id):
            child_pipe_end.put([task_id, g.value])
            
        def loop(child_pipe_end):
            while 1:
                f, args, kwargs, task_id = child_pipe_end.get()
                if task_id:
                    g = gevent.spawn(f, *args, **kwargs)
                    cb = partial(callback, task_id=task_id)
                    g.link(cb)
                else:
                    gevent.spawn(f, *args, **kwargs)
                    
        loop(child_pipe_end)

    def select_pipe_writer(self,  sn=None):
        if sn is not None:
            return self.parent_pipe_ends[sn]
        return random.choice(self.parent_pipe_ends)
        
    def _spawn(self, f, args=tuple(), kwargs={}, block=False, sn=None):
        """和gevent.spawn的区别是,如果block=False 就不返回任何值(gevent.spawn返回greenlet),如果block=True,返回f的结果值,而不是greenlet
        @param f: func
        @param args, kwargs: f的参数, ***必须能够pickle序列化***
        @param: block: True-等待f返回结果, False-不等待f返回结果
        """
        parent_pipe_end = self.select_pipe_writer(sn)
        if block:
            task_id = self.id_generator.next()
            self.results[task_id] = Queue(maxsize=1)
            parent_pipe_end.put([f, args, kwargs, task_id])
            result = self.results[task_id].get()
            del self.results[task_id]
            return result
        else:
            parent_pipe_end.put([f, args, kwargs, None])
        
    def spawn_block(self, f, *args, **kwargs):
        return self._spawn(f, args, kwargs, True, None)
        
    def spawn_unblock(self, f, *args, **kwargs):
        return self._spawn(f, args, kwargs, False, None)
        
    def close_pipes(self):
        [g.kill() for g in self.loop_get_result_glets]
        [p.close() for p in self.parent_pipe_ends] # 管道一端关闭即可
        
    def __del__(self):
        self.close_pipes()
        
        
if __name__ == "__main__":
    def x(a):
        return a
        
    try:
        ppool = PPool(2)
        ppool.init()
        print ppool.spawn_block(x, "abc")
        print ppool.spawn_unblock(x, "def")
        
        gevent.wait()
    except KeyboardInterrupt:
        ppool.close_pipes()
    

        