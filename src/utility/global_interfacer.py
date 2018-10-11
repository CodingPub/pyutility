#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
sys.path.insert(0, '..')
from utility.singleton import Singleton
from utility.pyinterfacer import PyInterfacer

__all__ = ['GlobalInterfacer']


class GlobalInterfacer(object, metaclass=Singleton):

    def __init__(self):
        super(GlobalInterfacer, self).__init__()
        self.interfacer = PyInterfacer()

    @classmethod
    def request_string(cls, url, headers=None, data=None, method=None, encoding=None, cache=None, retryTimes=None):
        return GlobalInterfacer().interfacer.request_string(url,
                                                            headers=headers,
                                                            data=data,
                                                            method=method,
                                                            encoding=encoding,
                                                            cache=cache,
                                                            retryTimes=retryTimes)

    @classmethod
    def request_data(cls, url, headers=None, data=None, method=None, cache=False):
        return GlobalInterfacer().interfacer.request_data(url,
                                                          headers=headers,
                                                          data=data,
                                                          method=method,
                                                          cache=cache)

    @classmethod
    def download_file(cls, local_path, url, headers=None, data=None, method=None):
        return GlobalInterfacer().interfacer.download_file(local_path,
                                                           url,
                                                           headers=headers,
                                                           data=data,
                                                           method=method)

    @classmethod
    def revert_cookie(cls):
        GlobalInterfacer().interfacer.revert_cookie()

    @classmethod
    def save_cookie(cls):
        GlobalInterfacer().interfacer.save_cookie()


def main():
    url = 'https://www.baidu.com/'
    # content = GlobalInterfacer().interfacer.request_string(url)
    content = GlobalInterfacer.request_string(url)
    print(content)


if __name__ == '__main__':
    main()
