# -*- coding: utf-8 -*-

"""以协程的方式实现:延时调用,循环调用,超时调用
: 如果为了优化协程数,最好使用 gevent.Timeout(或者下面的 timeout | timeout_partial), 而不是使用 TimeoutMixin
"""

from gevent import Greenlet
import gevent


class Delay(object):
    """延迟对象
    """
    
    def __init__(self, f, *args, **kw):
        self.f = f
        self.args = args
        self.kw = kw
    
    def call(self):
        return self.f(*self.args, **self.kw)
    
    
class DelayCall(Greenlet):
    """以一个微线程的方式实现一个延时调用:
    def p(x):
        print x
    d = DelayCall(5, p, "xx")
    d.start() # 会执行 d._run
    """
    
    def __init__(self, seconds, f, *args, **kw):
        Greenlet.__init__(self)
        self.seconds = seconds
        self.delay = Delay(f, *args, **kw)
        
    def cancel(self):
        """取消延时调用
        """
        self.kill()
        
    def _run(self):
        gevent.sleep(self.seconds)
        return self.delay.call()
    
    
class LoopingCall(Greenlet):
    """以一个微线程的方式实现一个定时调用:
    def p(x):
        print x
    lc = LoopingCall(5, p, "xx")
    lc.start() # 会执行 d._run
    # some condition
    lc.cancel()
    """
    
    def __init__(self, seconds, f, *args, **kw):
        Greenlet.__init__(self)
        self.seconds = seconds
        self.delay = Delay(f, *args, **kw)
        
    def cancel(self):
        """取消定时调用
        """
        self.kill()
        
    def _run(self):
        while True:
            gevent.sleep(self.seconds)
            self.delay.call()


class Timeout(gevent.Timeout):
    """和gevent.Timeout 相比增加了已经过去的时间和剩余时间属性"""
    
    def __init__(self, seconds=None, exception=None):
        gevent.Timeout.__init__(self, seconds, exception)
        self.stime = None
    
    def start(self):
        self.stime = time.time()
        gevent.Timeout.start(self)
    
    @property
    def passed(self):
        if self.stime is None: return 0
        now = time.time()
        return now - self.stime
    
    @property
    def rest(self):
        if self.stime is None: return 0
        if self.seconds is None: return 0
        now = time.time()
        return self.seconds - (now - self.stime)
    

class TimeoutMixin(object):
    """以一个微线程的方式实现一个超时调用:
    class Test(TimeoutMixin):
        
        def __init__(self):
            self.set_timeout(180)
            
        def on_timeout(self):
            print "timeout..."
    # 如果在180s内没有调用self.reset_timeout,或者self.set_timeout, 则会触发 on_timeout 被调用
    """
    
    dc = None
    start_flag = 0
    
    def set_timeout(self, seconds):
        """可以重新设置超时时间"""
        if self.start_flag == 1: self.cancel()
        self.seconds = seconds
        self.dc = DelayCall(seconds, self.on_timeout)
        self.dc.start()
        self.start_flag = 1
    
    def on_timeout(self):
        raise NotImplementedError
     
    def cancel(self):
        self.dc.cancel()
        self.start_flag = 0
        
    def reset_timeout(self):
        """重置超时
        """
        assert self.start_flag == 1
        self.dc.cancel()
        self.dc = DelayCall(self.seconds, self.on_timeout)
        self.dc.start()
        

def timeout(seconds=None, errback=None):
    """和 TimeoutMixin 相比,1.没有另开使用协程,2.使用装饰器, 效率高点
    : 超时/其他异常会调用cb
    : 注: 这个必须装饰阻塞函数(交出greenlet)上面才有效, TimeoutMixin 则没有限制
    @timeout(5)
    def test():
        gevent.sleep(8)
        return "test"
    ret = test()
    if isinstance(ret, BaseException):
        print "timeout..."
    """
    
    def wrapper(func):
        def _wrapper(*args, **kw):
            timer = None
            if seconds is not None:
                timer = gevent.Timeout(seconds)
                timer.start()
            try:
                ret = func(*args, **kw)
            except gevent.Timeout as t:
                assert timer == t, t
                if errback: errback(t)
                print "Timeout!"
                return t
            finally:
                if timer:
                    timer.cancel()
            return ret
        return _wrapper
    return wrapper

def timeout_partial(seconds=None, func=None, *args, **kw):
    """和上面 timeout 类似, 只是不是使用装饰器
    def test():
        gevent.sleep(5)
    ret = timeout_partial(3, test)
    if isinstance(ret, BaseException):
        print "timeout..."
    """
    timer = None
    if seconds is not None:
        timer = gevent.Timeout(seconds)
        timer.start()
    try:
        ret = func(*args, **kw)
    except gevent.Timeout as t:
        assert timer == t, t
        print "Timeout!"
        return t
    finally:
        if timer:
            timer.cancel()
    return ret
        
            
if __name__ == "__main__":
    
    
    class TestTimeout(TimeoutMixin):
          
        def __init__(self):
            self.set_timeout(10)
              
        def on_timeout(self):
            print "timeout..."
              
    tt = TestTimeout()
    
    @timeout(3)
    def test():
        gevent.sleep(5)
        return 2
    ret = test()
    print type(ret)
    print isinstance(ret, BaseException)
    
    def test2():
        gevent.sleep(5)
    print "t:", timeout_partial(3, test2) 
    
    gevent.wait()
        