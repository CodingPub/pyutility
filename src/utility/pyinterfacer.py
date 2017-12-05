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
from utility.common import Common
from utility.log import Log
from utility.gzip_util import GZip

__author__ = 'Lin Xiaobin'

__all__ = ['PyInterfacer']


class PyInterfacer(object):
    def __init__(self, cookiename=None):
        super(PyInterfacer, self).__init__()
        if cookiename is None:
            self.cookiename = 'cookie_default'
        else:
            self.cookiename = cookiename

        self.cookiejar = None
        self.opener = None

    def request_string(self, url, headers=None, data=None, method=None, encoding=None, cache=None,  retryTimes=None):
        if not retryTimes:
            retryTimes = 1
        if cache is None:
            cache = Common.debug()

        response = None
        for _ in range(retryTimes):
            response = self.request_data(url, headers=headers, data=data, method=method, cache=cache)
            if response is not None:
                break

        s = None
        if response is not None:
            if encoding:
                s = Common.decode_data(response, encoding=encoding)
            else:
                s = Common.decode_data(response, encoding='utf-8')
                if not s:
                    s = Common.decode_data(response, encoding='gbk')
        return s

    def request_data(self, url, headers=None, data=None, method=None, cache=False):
        if not headers:
            headers = {}

        cachePath = None
        if cache:
            md5Str = url
            md5Str = md5Str + urllib.parse.urlencode(headers)
            cachePath = os.path.join(tempfile.gettempdir(), hashlib.md5(md5Str.encode('utf-8')).hexdigest())
            if os.path.isfile(cachePath):
                Log.debug('load cache: ' + cachePath + ' url:' + url)
                with open(cachePath, 'rb') as f:
                    return f.read()

        response = None
        req = urllib.request.Request(url, data=data, headers=headers, origin_req_host=None, unverifiable=False, method=method)
        # 停止使用 Proxy
        # self.rebuildOpener(proxy={'http': proxy})
        self.rebuildOpener(proxy=None)
        try:
            with self.opener.open(req, timeout=30) as f:
                response = f.read()

                headers = f.info()
                encoding = headers.get('Content-Encoding')
                if encoding is not None and encoding == 'gzip' and isinstance(response, bytes):
                    response = GZip.uncompress(response)
        except Exception as e:
            Log.debug('request error: %s, %s' % (e, url))

        if response and cachePath:
            with open(cachePath, 'wb') as f:
                f.write(response)

        return response

    def cookiePath(self):
        if self.cookiename:
            return Common.join_paths(tempfile.gettempdir(), '%s.txt' % self.cookiename)
        else:
            return None

    def rebuildOpener(self, proxy=None):
        path = self.cookiePath()
        if self.cookiejar is None and path is not None:
            Log.debug('initialCookie: ' + path)
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

    def revert_cookie(self):
        path = self.cookiePath()
        if os.path.isfile(path) and self.cookiejar:
            self.cookiejar.revert(path)

    def save_cookie(self):
        if self.cookiejar:
            self.cookiejar.save(self.cookiePath())


# auto clean cache file before 1 week
Common.cleanTempDirectory(tempfile.gettempdir(), interval=7 * 24 * 60 * 60)


def main():
    # i1 = PyInterfacer('cookie1')
    # i1.request_data('https://github.com')
    # i1.saveCookie()

    # i2 = PyInterfacer('cookie2')
    # i2.request_data('https://www.baidu.com')
    # i2.saveCookie()

    i3 = PyInterfacer()
    s = i3.request_string('https://www.baidu.com/', cache=False)
    print(s)
    i3.save_cookie()


if __name__ == '__main__':
    main()
