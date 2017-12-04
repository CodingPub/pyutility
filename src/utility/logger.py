#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import logging.config
import logging.handlers
import sys
import os

sys.path.insert(0, '..')
from utility.singleton import Singleton

__all__ = ['Log']


class Log(object, metaclass=Singleton):
    def __init__(self):
        super(Log, self).__init__()
        self.logger = self.create_logger()

    @classmethod
    def info(cls, msg, *args, **kwargs):
        Log().logger.info(msg, *args, **kwargs)

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        Log().logger.debug(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg, *args, **kwargs):
        Log().logger.warning(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        Log().logger.error(msg, *args, **kwargs)

    def create_logger(self):
        dir_root = os.path.split(sys.argv[0])[0]
        dir_log = os.path.join(dir_root, 'log')

        if not os.path.isdir(dir_log):
            os.makedirs(dir_log)

        log_path = os.path.join(dir_log, 'log')

        fmt_str = '%(asctime)s(%(levelname)s): %(message)s'

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s(%(levelname)s): %(message)s',
                            datefmt='%Y/%m/%d %H:%M:%S')

        logger = logging.getLogger(name='main')

        # 每天创建一个日志文件，保留最近10个日志文件
        fileshandle = logging.handlers.TimedRotatingFileHandler(
            log_path, when='midnight', interval=1, backupCount=10)
        fileshandle.suffix = "%Y%m%d.txt"
        fileshandle.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt_str)
        fileshandle.setFormatter(formatter)
        logger.addHandler(fileshandle)

        return logger


if __name__ == '__main__':
    # close_file_log()

    for x in range(1, 2):
        Log.debug('debug %s %s', 'a', 'b')
        Log.info('info %s %s', 'a', 'b')
        Log.warning('warn %s %s', 'a', 'b')
        Log.error('error %s %s', 'a', 'b')
