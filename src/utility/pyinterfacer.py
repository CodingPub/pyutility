#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import tempfile
import hashlib
import http.cookiejar
import urllib.request
import ssl
sys.path.insert(0, '..')
from utility.common import *
from utility.logger import *
from utility.proxy import *
from utility.gzip_util import *


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
        # if self.cookiename:
        #     self.initialCookie()

    def requestString(self, url, headers=None, data=None, method=None, encoding=None, cache=None, randProxy=False, retryTimes=1):
        if cache is None:
            cache = isDebug()

        response = None
        for x in range(retryTimes):
            response = self.requestData(url, headers=headers, data=data, method=method, cache=cache, randProxy=randProxy)
            if response is not None:
                break

        s = None
        if response is not None:
            if encoding:
                s = decodeData(response, encoding=encoding)
            else:
                s = decodeData(response, encoding='utf-8')
                if not s:
                    s = decodeData(response, encoding='gbk')
        return s

    def requestData(self, url, headers=None, data=None, method=None, cache=False, randProxy=False):
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
        if randProxy:
            proxy = ProxyPool().randProxy()
            # print(proxy)
            self.rebuildOpener(proxy={'http': proxy})
        else:
            self.rebuildOpener(proxy=None)
        try:
            with self.opener.open(req, timeout=30) as f:
                response = f.read()

                headers = f.info()
                encoding = headers.get('Content-Encoding')
                if encoding is not None and encoding == 'gzip' and isinstance(response, bytes):
                    response = gzip_uncompress(response)
        except Exception as e:
            logger.debug('request error: %s, %s' % (e, url))
            if randProxy and proxy:
                # print('check proxy:', proxy)
                ProxyPool().vertifyProxy(proxy, times=1)

        if response and cachePath:
            with open(cachePath, 'wb') as f:
                f.write(response)

        return response

    def cookiePath(self):
        if self.cookiename:
            return joinPaths(tempfile.gettempdir(), '%s.txt' % self.cookiename)
        else:
            return None

    def rebuildOpener(self, proxy=None):
        path = self.cookiePath()
        if self.cookiejar is None and path is not None:
            logger.debug('initialCookie: ' + path)
            cj = http.cookiejar.MozillaCookieJar()
            self.cookiejar = cj
            if os.path.isfile(path):
                cj.load(path)

        hcj = urllib.request.HTTPCookieProcessor(self.cookiejar)

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        context = urllib.request.HTTPSHandler(context=ctx)

        args = [hcj, context]
        if proxy:
            args.append(urllib.request.ProxyHandler(proxy))

        opener = urllib.request.build_opener(*args)
        self.opener = opener

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


def requestString(url, headers=None, data=None, method=None, encoding=None, cache=None, randProxy=False, retryTimes=1):
    global _interfacer
    return _interfacer.requestString(url, headers=headers, data=data, method=method, encoding=encoding, cache=cache, randProxy=randProxy, retryTimes=retryTimes)


def requestData(url, headers=None, data=None, method=None, cache=False, randProxy=False):
    global _interfacer
    return _interfacer.requestData(url, headers=headers, data=data, method=method, cache=cache, randProxy=randProxy)


# auto clean cache file before 1 week
cleanTempDirectory(tempfile.gettempdir(), interval=7 * 24 * 60 * 60)


if __name__ == '__main__':
    # i1 = PyInterfacer('cookie1')
    # i1.requestData('https://github.com')
    # i1.saveCookie()

    # i2 = PyInterfacer('cookie2')
    # i2.requestData('https://www.baidu.com')
    # i2.saveCookie()

    i3 = PyInterfacer()
    s = i3.requestString('https://giphy.com/page/2?next=2017-05-02%2015%3A30%3A01&amp%3Bis=1&is=1&json=true')
    # print(s)
    i3.saveCookie()

    pass
