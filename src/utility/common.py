#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import json
import threading
import re
import time
import hashlib
from lxml import etree

sys.path.insert(0, '.')
from utility.log import Log
from utility.singleton import Singleton

__author__ = 'Lin Xiaobin'

__all__ = ['Common']


class Common(object, metaclass=Singleton):

    def __init__(self):
        super(Common, self).__init__()
        self.is_debug = False
        self.cmdlock = threading.Lock()

    @classmethod
    def debug(cls):
        return Common().is_debug

    @classmethod
    def set_debug(cls, debug):
        Common().is_debug = debug

    @classmethod
    def add_sys_path(cls, path):
        if os.path.isdir(path):
            sys.path.insert(0, path)
        elif path:
            sys.path.insert(0, os.path.split(path)[0])

    @classmethod
    def get_cmd_dir(cls):
        path = os.path.abspath(sys.argv[0])
        path = os.path.split(path)[0]
        return path

    @classmethod
    def join_paths(cls, *paths):
        if not paths:
            return None

        r = paths[0]
        for i in range(1, len(paths)):
            r = os.path.join(r, paths[i])

        return r

    @classmethod
    def split_path(cls, path, level=1):
        if path is None or level <= 0:
            return path

        result = os.path.split(path)
        curIdx = 1
        while curIdx < level and result and len(result) == 2:
            result = os.path.split(result[0])
            curIdx += 1
        return result

    @classmethod
    def abs_path(cls, path):
        if path is None:
            return

        return os.path.abspath(path)

    @classmethod
    def file_dir(cls, path):
        arr = cls.split_path(cls.abs_path(path), level=1)
        if arr and len(arr) >= 1:
            return arr[0]
        return None

    @classmethod
    def filename(cls, path):
        arr = cls.split_path(path, level=1)
        if arr and len(arr) >= 1:
            arr = os.path.splitext(arr[1])
            if arr and len(arr) >= 1:
                return arr[0]
        return None

    @classmethod
    def file_extension(cls, path):
        if path is None:
            return

        arr = os.path.splitext(path)
        if arr and len(arr) >= 1:
            return arr[1]
        return arr

    @classmethod
    def create_dir(cls, directory):
        if not os.path.isdir(directory):
            os.makedirs(directory)

    @classmethod
    def create_dirs(cls, dirs):
        if dirs:
            for d in dirs:
                cls.create_dir(d)

    @classmethod
    def remove(cls, path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
        except IOError as e:
            if cls.debug():
                Log.debug(e)

    @classmethod
    def isfile(cls, path):
        if path:
            return os.path.isfile(path)
        return False

    @classmethod
    def isdir(cls, path):
        if path:
            return os.path.isdir(path)
        return False

    @classmethod
    def rex_matching(cls, pattern, string, flags=0):
        result = None
        if string and pattern:
            try:
                result = re.match(pattern, string, flags=flags)
            except Exception as e:
                Log.debug('something error: %s' % e)

        return result

    @classmethod
    def rex_search(cls, pattern, string, flags=0):
        result = None
        if string and pattern:
            try:
                result = re.search(pattern, string, flags=flags)
            except Exception as e:
                Log.debug('something error: %s' % e)

        return result

    @classmethod
    def rex_find_all(cls, pattern, string, flags=0):
        result = None
        if string and pattern:
            try:
                result = re.findall(pattern, string, flags=flags)
            except Exception as e:
                Log.debug('something error: %s' % e)

        return result

    @classmethod
    def list_dir(cls, directory, nameRex=None, extRex=None, justFile=False, justDir=False):
        result = []
        if directory and os.path.isdir(directory):
            files = os.listdir(directory)

            for file in files:
                name, ext = os.path.splitext(file)
                abs_path = os.path.abspath(cls.join_paths(directory, file))
                isdir = os.path.isdir(abs_path)
                if justFile and isdir:
                    continue
                if justDir and not isdir:
                    continue

                add = True
                if nameRex and extRex:
                    add = cls.rex_matching(nameRex, name) and cls.rex_matching(extRex, ext)
                elif nameRex:
                    add = cls.rex_matching(nameRex, name)
                elif extRex:
                    add = cls.rex_matching(extRex, ext)

                if add:
                    result.append(file)

        return result

    @classmethod
    def cleanTempDirectory(cls, directory, interval=7 * 24 * 60 * 60, sync=False):
        if sync:
            cls._cleanTempDirectory(directory, interval)
        else:
            t = threading.Thread(target=cls._cleanTempDirectory, args=(directory, interval))
            t.start()

    @classmethod
    def _cleanTempDirectory(cls, directory, interval):
        array = cls.list_dir(directory, nameRex=None, extRex=None, justFile=True, justDir=False)
        for x in array:
            path = cls.join_paths(directory, x)
            if os.access(path, os.W_OK):
                ctime = os.path.getmtime(path)
                current = time.time()
                if current - ctime >= interval:
                    cls.remove(path)

    @classmethod
    def read_file(cls, file, encoding='utf-8'):
        try:
            with open(file, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            Log.warning('%s: %s' % (e, file))

    @classmethod
    def write_file(cls, file, string, mode='w', encoding='utf-8'):
        try:
            with open(file, mode, encoding=encoding) as f:
                f.write(string)
        except Exception as e:
            Log.warning('%s: %s' % (e, file))

    @classmethod
    def write_data(cls, file, data):
        try:
            with open(file, 'wb') as f:
                f.write(data)
        except Exception as e:
            Log.warning('%s: %s' % (e, file))

    @classmethod
    def replace_file(cls, src, dst):
        if os.path.isdir(src):
            cls.remove(dst)
            shutil.copytree(src, dst)
        elif os.path.isfile(src):
            cls.remove(dst)
            shutil.copyfile(src, dst)

    @classmethod
    def html_elements(cls, content, xpath, tree=None):
        if not content or not xpath:
            return None

        elements = []
        try:
            if tree is not None:
                tree = etree.HTML(content)
            elements = tree.xpath(xpath)
        except Exception as e:
            print('xpath except: ', e)

        return elements

    @classmethod
    def first_xpath(cls, content, xpath, tree=None):
        elements = cls.html_elements(content, xpath, tree=tree)
        if elements:
            return elements[0]
        return None

    @classmethod
    def encode_data(cls, string, encoding='utf-8'):
        data = None
        if string is None:
            return data

        try:
            data = bytes(string, encoding)
        except Exception as e:
            raise e

        return data

    @classmethod
    def decode_data(cls, data, encoding='utf-8'):
        s = None
        if data:
            try:
                s = data.decode(encoding)
            except Exception as e:
                print(e)
        return s

    @classmethod
    def str2json(cls, string):
        result = None
        if string:
            try:
                result = json.loads(string)
            except Exception as e:
                if cls.debug():
                    Log.debug('str2json:%s' % e)

        return result

    @classmethod
    def json2str(cls, jsonStr):
        result = None
        if jsonStr:
            try:
                result = json.dumps(jsonStr, ensure_ascii=False, indent=2)
            except Exception as e:
                if cls.debug():
                    Log.debug('json2str:%s' % e)

        return result

    @classmethod
    def md5(cls, string):
        if string is None:
            return None

        return hashlib.md5(string.encode('utf-8')).hexdigest()

    @classmethod
    def json_list2item_list(cls, jsonArr, selector):
        result = []
        if jsonArr:
            for x in jsonArr:
                w = selector(x)
                if w:
                    result.append(w)
        return result

    @classmethod
    def system_cmd(cls, cmd, directory=None, log=False):
        lock = Common().cmdlock
        lock.acquire()

        if directory is not None:
            os.chdir(directory)
        if cls.debug():
            Log.debug(cmd)

        result = None
        if log:
            r = os.popen(cmd)
            result = r.read()
            r.close()
        else:
            result = os.system(cmd)

        lock.release()

        return result

    @classmethod
    def multi_run(cls, target, array, threadCount, beginMsg, finishMsg, args=None):
        if beginMsg:
            Log.info(beginMsg)
        ts = []

        if array is not None and threadCount > len(array):
            threadCount = len(array)

        for idx in range(0, threadCount):
            t = threading.Thread(target=cls.run_method,
                                 args=[target, array, idx, threadCount, args])
            t.setDaemon(True)
            t.start()
            ts.append(t)
        for t in ts:
            t.join()

        if finishMsg:
            Log.info(finishMsg)

    @classmethod
    def run_method(cls, target, array, begin, step, kw):
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

    print(Common.debug())
    Common.set_debug(True)
    print(Common.debug())
