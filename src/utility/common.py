#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import json
import threading
import re
import time
from utility.logger import *
from lxml import etree


__author__ = 'Lin Xiaobin'

__all__ = ['isDebug', 'setDebug',
           'addsyspath',
           'cmddir', 'joinPaths', 'splitPath',
           'createdir', 'createdirs', 'remove',
           'isfile', 'isdir',
           'listdir',
           'cleanTempDirectory',
           'readfile', 'writefile', 'replacefile',
           'decodeData',
           'htmlElements', 'firstxpath',
           'rexMatching', 'rexSearch',
           'str2Json', 'json2Str',
           'systemCmd',
           'multiRun']


DEBUG = False


def isDebug():
    return DEBUG


def setDebug(debug):
    global DEBUG
    DEBUG = debug


def addsyspath(path):
    if os.path.isdir(path):
        sys.path.insert(0, path)
    elif path:
        sys.path.insert(0, os.path.split(path)[0])


def cmddir():
    path = os.path.abspath(sys.argv[0])
    path = os.path.split(path)[0]
    return path


def joinPaths(*paths):
    if paths is None or len(paths) == 0:
        return None

    r = paths[0]
    for i in range(1, len(paths)):
        r = os.path.join(r, paths[i])

    return r


def splitPath(path, level=1):
    if path is None or level <= 0:
        return path

    result = os.path.split(path)
    curIdx = 1
    while curIdx < level and result and len(result) == 2:
        result = os.path.split(result[0])
        curIdx += 1
    return result


def createdir(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)


def createdirs(dirs):
    if dirs and len(dirs) > 0:
        for d in dirs:
            createdir(d)


def remove(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
    except Exception as e:
        if isDebug():
            logger.debug(e)


def isfile(path):
    if path:
        return os.path.isfile(path)
    return False


def isdir(path):
    if path:
        return os.path.isdir(path)
    return False


def rexMatching(pattern, string, flags=0):
    result = None
    if string and pattern:
        try:
            result = re.match(pattern, string, flags=flags)
        except Exception as e:
            logger.debug('something error: %s' % e)

    return result


def rexSearch(pattern, string, flags=0):
    result = None
    if string and pattern:
        try:
            result = re.search(pattern, string, flags=flags)
        except Exception as e:
            logger.debug('something error: %s' % e)

    return result


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


def cleanTempDirectory(directory, interval=7 * 24 * 60 * 60, sync=False):
    if sync:
        _cleanTempDirectory(directory, interval)
    else:
        t = threading.Thread(target=_cleanTempDirectory, args=(directory, interval))
        t.start()


def _cleanTempDirectory(directory, interval):
    array = listdir(directory, nameRex=None, extRex=None, justFile=True, justDir=False)
    for x in array:
        path = joinPaths(directory, x)
        ctime = os.path.getmtime(path)
        current = time.time()
        if current - ctime >= interval:
            remove(path)


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
        os.chdir(directory)
    if isDebug():
        logger.debug(cmd)

    if log:
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text
    else:
        return os.system(cmd)


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

    if finishMsg:
        logger.info(finishMsg)


def runMethod(target, array, begin, step):
    curIdx = begin
    if array is None or curIdx >= len(array):
        return

    while True:
        target(array, curIdx)
        curIdx += step
        if curIdx >= len(array):
            break


if __name__ == '__main__':

    pass
