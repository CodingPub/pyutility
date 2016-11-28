#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import tempfile
import http.cookiejar
import urllib.request
from utility.common import *
from utility.logger import *

__author__ = 'Lin Xiaobin'

__all__ = ['requestString', 'requestData',
           'revertCookie', 'saveCookie',
           'PyInterfacer']


class PyInterfacer(object):
    def __init__(self, cookiename=None):
        super(PyInterfacer, self).__init__()
        if cookiename is None:
            self.cookiename = 'cookie_default'
        else:
            self.cookiename = cookiename

        self.cookiejar = None
        self.opener = None
        if self.cookiename:
            self.initialCookie()

    def requestString(self, url, headers=None, data=None, method=None, encoding=None, cache=True):
        data = self.requestData(url, headers=headers, data=data, method=method, cache=cache)
        s = None
        if data:
            if encoding:
                s = decodeData(data, encoding=encoding)
            else:
                s = decodeData(data, encoding='utf-8')
                if not s:
                    s = decodeData(data, encoding='gbk')
        return s

    def requestData(self, url, headers=None, data=None, method=None, cache=False):
        if not headers:
            headers = {}

        cachePath = None
        if cache:
            md5Str = url
            md5Str = md5Str + urllib.parse.urlencode(headers)
            cachePath = os.path.join(tempfile.gettempdir(), hashlib.md5(md5Str.encode('utf-8')).hexdigest())
            if os.path.isfile(cachePath):
                logger.debug('load cache: ' + cachePath + ' url:' + url)
                with open(cachePath, 'rb') as f:
                    return f.read()

        response = None
        req = urllib.request.Request(url, data=data, headers=headers, origin_req_host=None, unverifiable=False, method=method)
        try:
            with self.opener.open(req) as f:
                response = f.read()
        except Exception as e:
            logger.warning('request error: %s, %s' % (e, url))

        if response and cachePath:
            with open(cachePath, 'wb') as f:
                f.write(response)

        return response

    def cookiePath(self):
        if self.cookiename:
            return joinPaths(tempfile.gettempdir(), '%s.txt' % self.cookiename)
        else:
            return None

    def initialCookie(self):
        path = self.cookiePath()
        if self.cookiejar is None and path is not None:
            logger.info('initialCookie: ' + path)
            cj = http.cookiejar.MozillaCookieJar()
            self.cookiejar = cj
            if os.path.isfile(path):
                cj.load(path)

            hcj = urllib.request.HTTPCookieProcessor(cj)
            opener = urllib.request.build_opener(hcj)
            self.opener = opener
            # urllib.request.install_opener(opener)

    def revertCookie(self):
        path = self.cookiePath()
        if os.path.isfile(path):
            self.cookiejar.revert(path)

    def saveCookie(self):
        if self.cookiejar is not None:
            self.cookiejar.save(self.cookiePath())


_interfacer = PyInterfacer()


def revertCookie():
    global _interfacer
    _interfacer.revertCookie()


def saveCookie():
    global _interfacer
    _interfacer.saveCookie()


def requestString(url, headers=None, data=None, method=None, encoding=None, cache=True):
    global _interfacer
    return _interfacer.requestString(url, headers=headers, data=data, method=method, encoding=encoding, cache=cache)


def requestData(url, headers=None, data=None, method=None, cache=False):
    global _interfacer
    return _interfacer.requestData(url, headers=headers, data=data, method=method, cache=cache)


if __name__ == '__main__':
    i1 = PyInterfacer('cookie1')
    i1.requestData('http://www.baidu.com')
    i1.requestData('https://github.com')
    i1.saveCookie()

    i2 = PyInterfacer('cookie2')
    i2.requestData('http://www.baidu.com')
    i2.saveCookie()

    i3 = PyInterfacer()
    i3.requestData('http://www.baidu.com')
    i3.saveCookie()

    pass
