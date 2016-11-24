#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading


__all__ = ['singleton', 'Singleton']


# 装饰器方式，不能继续继承单例
def singleton(cls, *args, **kw):
    _instances = {}
    _lock = threading.Lock()

    def _singleton(*args, **kw):
        _lock.acquire()

        if cls not in _instances:
            _instances[cls] = cls(*args, **kw)

        _lock.release()
        return _instances[cls]

    return _singleton


# metaclass 方式，可继承单例
# 例如：
# class ClassA(object, metaclass=Singleton):
# class ClassB(ClassA)
class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance


if __name__ == '__main__':

    pass
