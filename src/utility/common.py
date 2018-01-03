'''
common.py 提供了一些常用方法
'''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import json
import os
import re
import shutil
import sys
import threading
import time

from lxml import etree
from utility.logger import logger

sys.path.insert(0, '..')

__author__ = 'Lin Xiaobin'

__all__ = ['isDebug', 'setDebug',
           'addsyspath',
           'cmddir', 'joinPaths', 'splitPath', 'absPath', 'filedir', 'filename', 'fileExtension',
           'createdir', 'createdirs', 'remove',
           'isfile', 'isdir',
           'listdir',
           'cleanTempDirectory',
           'readfile', 'writefile', 'replacefile',
           'decodeData', 'encodeData',
           'htmlElements', 'firstxpath',
           'rexMatching', 'rexSearch', 'rexFindAll',
           'str2Json', 'json2Str',
           'md5',
           'jsonArr2ItemArr',
           'systemCmd',
           'multiRun']


DEBUG = False


def isDebug():
    ''' 是否调试模式 '''
    return DEBUG


def setDebug(debug):
    ''' 修改调试模式 '''
    global DEBUG
    DEBUG = debug


def addsyspath(path):
    ''' 添加系统扫描路径 '''
    if os.path.isdir(path):
        sys.path.insert(0, path)
    elif path:
        sys.path.insert(0, os.path.split(path)[0])


def cmddir():
    ''' 获取 python 文件的当前目录 '''
    path = os.path.abspath(sys.argv[0])
    path = os.path.split(path)[0]
    return path


def joinPaths(*paths):
    ''' 拼接路径 '''
    if not paths:
        return None

    r = paths[0]
    for i in range(1, len(paths)):
        r = os.path.join(r, paths[i])

    return r


def splitPath(path, level=1):
    ''' 拆分路径，level 表示拆分的次数，返回最后一次的目录和文件名 '''
    if path is None or level <= 0:
        return path

    result = os.path.split(path)
    curIdx = 1
    while curIdx < level and result and len(result) == 2:
        result = os.path.split(result[0])
        curIdx += 1
    return result


def absPath(path):
    ''' 获取绝对路径 '''
    if path is None:
        return

    return os.path.abspath(path)


def filedir(path):
    ''' 获取文件所在目录 '''
    arr = splitPath(absPath(path), level=1)
    if arr and len(arr) >= 1:
        return arr[0]
    return None


def filename(path):
    ''' 获取文件名，不包含文件扩展名 '''
    arr = splitPath(path, level=1)
    if arr and len(arr) >= 1:
        arr = os.path.splitext(arr[1])
        if arr and len(arr) >= 1:
            return arr[0]
    return None


def fileExtension(path):
    ''' 获取文件扩展名 '''
    if path is None:
        return

    arr = os.path.splitext(path)
    if arr and len(arr) >= 1:
        return arr[1]
    return arr


def createdir(directory):
    ''' 创建目录 '''
    if not os.path.isdir(directory):
        os.makedirs(directory)


def createdirs(dirs):
    ''' 批量创建目录 '''
    if dirs:
        for d in dirs:
            createdir(d)


def remove(path):
    ''' 删除文件或目录 '''
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
    except Exception as e:
        if isDebug():
            logger.debug(e)


def isfile(path):
    ''' 判断路径是否存在文件 '''
    if path:
        return os.path.isfile(path)
    return False


def isdir(path):
    ''' 判断是否存在目录 '''
    if path:
        return os.path.isdir(path)
    return False


def rexMatching(pattern, string, flags=0):
    ''' 正则表达式匹配 '''
    result = None
    if string and pattern:
        try:
            result = re.match(pattern, string, flags=flags)
        except Exception as e:
            logger.debug('something error: %s', e)

    return result


def rexSearch(pattern, string, flags=0):
    ''' 正则表达式匹配 '''
    result = None
    if string and pattern:
        try:
            result = re.search(pattern, string, flags=flags)
        except Exception as e:
            logger.debug('something error: %s', e)

    return result


def rexFindAll(pattern, string, flags=0):
    ''' 正则匹配所有 '''
    result = None
    if string and pattern:
        try:
            result = re.findall(pattern, string, flags=flags)
        except Exception as e:
            logger.debug('something error: %s', e)

    return result


def listdir(directory, nameRex=None, extRex=None, justFile=False, justDir=False):
    '''
    扫描目录

    Attributes:
        directory 扫描目录
        nameRex 文件名正则
        extRex 扩展名正则
        justFile 只查找文件
        justDir 只查找文件夹
    '''
    result = []
    if directory and os.path.isdir(directory):
        files = os.listdir(directory)

        for aFile in files:
            name, ext = os.path.splitext(aFile)
            abs_path = os.path.abspath(joinPaths(directory, aFile))
            is_dir = os.path.isdir(abs_path)
            if justFile and is_dir:
                continue
            if justDir and not is_dir:
                continue

            add = True
            if nameRex and extRex:
                add = rexMatching(nameRex, name) and rexMatching(extRex, ext)
            elif nameRex:
                add = rexMatching(nameRex, name)
            elif extRex:
                add = rexMatching(extRex, ext)

            if add:
                result.append(aFile)

    return result


def cleanTempDirectory(directory, interval=7 * 24 * 60 * 60, sync=False):
    ''' 清理缓存目录 '''
    if sync:
        _cleanTempDirectory(directory, interval)
    else:
        t = threading.Thread(target=_cleanTempDirectory,
                             args=(directory, interval))
        t.start()


def _cleanTempDirectory(directory, interval):
    array = listdir(directory, nameRex=None, extRex=None,
                    justFile=True, justDir=False)
    for x in array:
        path = joinPaths(directory, x)
        if os.access(path, os.W_OK):
            ctime = os.path.getmtime(path)
            current = time.time()
            if current - ctime >= interval:
                remove(path)


def readfile(file_path, encoding='utf-8'):
    ''' 读文件，返回字符串 '''
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.warning('%s: %s', e, file_path)


def writefile(file_path, string, mode='w', encoding='utf-8'):
    ''' 写文件，写入字符串 '''
    try:
        with open(file_path, mode, encoding=encoding) as f:
            f.write(string)
    except Exception as e:
        logger.warning('%s: %s', e, file_path)


def replacefile(src, dst):
    ''' 替换文件 '''
    if os.path.isdir(src):
        remove(dst)
        shutil.copytree(src, dst)
    elif os.path.isfile(src):
        remove(dst)
        shutil.copyfile(src, dst)


def htmlElements(content, xpath):
    ''' 从字符串中提取 xpath 元素列表 '''
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
    ''' 从字符串中提取第一个 xpath 元素 '''
    elements = htmlElements(content, xpath)
    if elements:
        return elements[0]

    return None


def encodeData(string, encoding='utf-8'):
    ''' 字符串编码 '''
    data = None
    if string is None:
        return data

    try:
        data = bytes(string, encoding)
    except Exception as e:
        raise e

    return data


def decodeData(data, encoding='utf-8'):
    ''' 字符串解码 '''
    s = None
    if data:
        try:
            s = data.decode(encoding)
        except Exception as e:
            print(e)
    return s


def str2Json(string):
    ''' 字符串转 json '''
    result = None
    if string:
        try:
            result = json.loads(string)
        except Exception as e:
            if isDebug():
                logger.debug('str2Json:%s', e)

    return result


def json2Str(jsonStr):
    ''' json 转字符串 '''
    result = None
    if jsonStr:
        try:
            result = json.dumps(jsonStr, ensure_ascii=False, indent=2)
        except Exception as e:
            if isDebug():
                logger.debug('json2Str:%s', e)

    return result


def md5(string):
    ''' 计算字符串 md5 值 '''
    if string is None:
        return None

    return hashlib.md5(string.encode('utf-8')).hexdigest()


def jsonArr2ItemArr(jsonArr, selector):
    ''' json list 批量转换 '''
    result = []
    if jsonArr:
        for x in jsonArr:
            w = selector(x)
            if w:
                result.append(w)
    return result


_cmdlock = threading.Lock()


def systemCmd(cmd, directory=None, log=False):
    ''' 执行命令行方法 '''
    _cmdlock.acquire()

    if directory is not None:
        os.chdir(directory)
    if isDebug():
        logger.debug(cmd)

    result = None
    if log:
        r = os.popen(cmd)
        result = r.read()
        r.close()
    else:
        result = os.system(cmd)

    _cmdlock.release()

    return result


def multiRun(target, array, threadCount, beginMsg, finishMsg, args=None):
    ''' 多线程运行 '''
    if beginMsg:
        logger.info(beginMsg)
    ts = []

    if array is not None and threadCount > len(array):
        threadCount = len(array)

    for idx in range(0, threadCount):
        t = threading.Thread(target=_runMethod,
                             args=[target, array, idx, threadCount, args])
        t.setDaemon(True)
        t.start()
        ts.append(t)
    for t in ts:
        t.join()

    if finishMsg:
        logger.info(finishMsg)


def _runMethod(target, array, begin, step, kw):
    curIdx = begin

    if array is None:
        while True:
            result = target(curIdx, args=kw)
            if result is None or not result:
                break
            curIdx += step
    elif curIdx < len(array):
        while curIdx < len(array):
            target(array, curIdx, args=kw)
            curIdx += step


if __name__ == '__main__':
    l = ''
    if l:
        print('true')
    else:
        print('false')
