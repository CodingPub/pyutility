#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading


__all__ = ['singleton']


def singleton(cls, *args, **kw):
    _instances = {}
    _lock = threading.Lock()

    def _singleton(*args, **kw):
        _lock.acquire()

        if cls not in _instances:
            print(cls)
            print(args)
            print(kw)

            _instances[cls] = cls(*args, **kw)

        _lock.release()
        return _instances[cls]

    return _singleton


if __name__ == '__main__':

    @singleton
    class ClassA(object):
        def __init__(self, arg1, t=None):
            # super(ClassA, self).__init__()
            self.arg1 = arg1
            self.t = t
            pass

    print(ClassA(12, t='a'))
    print(ClassA())
    print(ClassA().arg1)
    print(ClassA().t)
