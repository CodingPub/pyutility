#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading

__all__ = ['singleton']


def singleton(cls, *args, **kw):
    _instances = {}
    _lock = threading.Lock()

    def _singleton():
        _lock.acquire()

        if cls not in _instances:
            _instances[cls] = cls(*args, **kw)

        _lock.release()
        return _instances[cls]

    return _singleton


if __name__ == '__main__':

    @singleton
    class ClassA(object):
        pass

    print(ClassA())
    print(ClassA())


# <__main__.ClassA object at 0x101340550>
# <__main__.ClassA object at 0x101340550>
