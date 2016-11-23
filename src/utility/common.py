#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import hashlib
import shutil
import json
import threading
import http.cookiejar
import urllib.request
import re
from utility.logger import *
from lxml import etree


__author__ = 'Lin Xiaobin'

__all__ = ['isDebug', 'setDebug',
           'cmddir', 'joinPaths',
           'createdir', 'createdirs', 'remove',
           'isfile', 'isdir',
           'listdir',
           'readfile', 'writefile', 'replacefile',
           'requestString', 'requestData',
           'htmlElements', 'firstxpath',
           'str2Json', 'json2Str',
           'initialCookie', 'revertCookie', 'saveCookie',
           'systemCmd',
           'multiRun']


DEBUG = False


def isDebug():
    return DEBUG


def setDebug(debug):
    global DEBUG
    DEBUG = debug


def cmddir():
    path = os.path.split(sys.argv[0])[0]
    return path


def joinPaths(*paths):
    if paths is None or len(paths) == 0:
        return None

    r = paths[0]
    for i in range(1, len(paths)):
        r = os.path.join(r, paths[i])

    return r


def createdir(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)


def createdirs(dirs):
    if dirs and len(dirs) > 0:
        for d in dirs:
            createdir(d)


def remove(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def isfile(path):
    if path:
        return os.path.isfile(path)
    return False


def isdir(path):
    if path:
        return os.path.isdir(path)
    return False


def rexMatching(pattern, string):
    if string and pattern:
        return re.match(pattern, string, flags=0)
    else:
        return None


def listdir(directory, nameRex=None, extRex=None, justFile=False, justDir=False):
    result = []
    if directory and os.path.isdir(directory):
        files = os.listdir(directory)

        for file in files:
            name, ext = os.path.splitext(file)
            absPath = os.path.abspath(joinPaths(directory, file))
            isdir = os.path.isdir(absPath)
            if justFile and isdir:
                continue
            if justDir and not isdir:
                continue

            add = True
            if nameRex and extRex:
                add = rexMatching(nameRex, name) and rexMatching(extRex, ext)
            elif nameRex:
                add = rexMatching(nameRex, name)
            elif extRex:
                add = rexMatching(extRex, ext)

            if add:
                result.append(file)

    return result


def readfile(file, encoding='utf-8'):
    try:
        with open(file, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.warning('%s: %s' % (e, file))


def writefile(file, string, encoding='utf-8'):
    try:
        with open(file, 'w', encoding=encoding) as f:
            f.write(string)
    except Exception as e:
        logger.warning('%s: %s' % (e, file))


def replacefile(src, dst):
    if os.path.isdir(src):
        remove(dst)
        shutil.copytree(src, dst)
    elif os.path.isfile(src):
        remove(dst)
        shutil.copyfile(src, dst)


def requestString(url, headers=None, data=None, method=None, encoding=None, cache=True):
    data = requestData(url, headers=headers, data=data, method=method, cache=cache)
    s = None
    if data:
        if encoding:
            s = decodeData(data, encoding=encoding)
        else:
            s = decodeData(data, encoding='utf-8')
            if not s:
                s = decodeData(data, encoding='gbk')
    return s


def requestData(url, headers=None, data=None, method=None, cache=False):
    if not headers:
        headers = {}
    md5Str = url
    md5Str = md5Str + urllib.parse.urlencode(headers)
    cachePath = os.path.join(tempfile.gettempdir(), hashlib.md5(md5Str.encode('utf-8')).hexdigest())

    if cache and os.path.isfile(cachePath):
        logger.debug('load cache: ' + cachePath + ' url:' + url)
        with open(cachePath, 'rb') as f:
            return f.read()

    response = None

    req = urllib.request.Request(url, data=data, headers=headers, origin_req_host=None, unverifiable=False, method=method)
    try:
        with urllib.request.urlopen(req) as f:
            response = f.read()
    except Exception as e:
        logger.warning('request error: %s' % e)

    if response and (cache):
        # if isDebug():
        #     logger.debug('write cache: ' + cachePath + ' url:' + url)
        with open(cachePath, 'wb') as f:
            f.write(response)

    return response


def htmlElements(content, xpath):
    if content is None or xpath is None:
        return None

    elements = []
    try:
        tree = etree.HTML(content)
        elements = tree.xpath(xpath)
    except Exception as e:
        print('xpath except: ', e)

    return elements


def firstxpath(content, xpath):
    elements = htmlElements(content, xpath)
    if elements and len(elements) > 0:
        return elements[0]
    else:
        return None


def decodeData(data, encoding='utf-8'):
    s = None
    if data:
        try:
            s = data.decode(encoding)
        except Exception as e:
            print(e)
    return s


def str2Json(string):
    result = None
    if string:
        try:
            result = json.loads(string)
        except Exception as e:
            if isDebug():
                logger.debug('str2Json:%s' % e)

    return result


def json2Str(jsonStr):
    result = None
    if jsonStr:
        try:
            result = json.dumps(jsonStr)
        except Exception as e:
            if isDebug():
                logger.debug('json2Str:%s' % e)

    return result


def systemCmd(cmd, directory=None, log=False):
    if directory is not None:
        cmd = 'cd %s;' % directory + '\n' + cmd
    if isDebug():
        logger.debug(cmd)

    if log:
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text
    else:
        return os.system(cmd)


_cookiejar = None


def cookiePath():
    return os.path.join(tempfile.gettempdir(), 'cookie.txt')


def initialCookie():
    global _cookiejar
    if _cookiejar is None:
        path = cookiePath()
        logger.info('initialCookie' + path)
        cj = http.cookiejar.MozillaCookieJar()
        _cookiejar = cj
        if os.path.isfile(path):
            cj.load(path)

        hcj = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(hcj)
        urllib.request.install_opener(opener)


def revertCookie():
    global _cookiejar
    path = cookiePath()
    if os.path.isfile(path):
        _cookiejar.revert(path)


def saveCookie():
    global _cookiejar
    _cookiejar.save(cookiePath())


def multiRun(target, array, threadCount, beginMsg, finishMsg):
    if beginMsg:
        logger.info(beginMsg)
    ts = []
    for idx in range(0, threadCount):
        args = (target, array, idx, threadCount)
        t = threading.Thread(target=runMethod, args=args)
        t.start()
        ts.append(t)
    for t in ts:
        t.join()

    if beginMsg:
        logger.info(finishMsg)


def runMethod(target, array, begin, step):
    curIdx = begin
    if curIdx >= len(array):
        return

    while target(array, curIdx):
        curIdx += step


if __name__ == '__main__':

    print(json2Str({'2': 2}))
    print(str2Json('{"2": 2}'))

    pass
