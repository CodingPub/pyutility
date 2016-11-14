#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.config
import logging.handlers
import sys
import os


dirRoot = os.path.split(sys.argv[0])[0]

dirLog = os.path.join(dirRoot, 'log')
if not os.path.isdir(dirLog):
    os.makedirs(dirLog)

filename = os.path.join(dirLog, 'current')

fmt_str = '%(asctime)s(%(levelname)s): %(message)s'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s(%(levelname)s): %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')

logger = logging.getLogger(name='main')

# 每天创建一个日志文件，保留最近10个日志文件
fileshandle = logging.handlers.TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=10)
fileshandle.suffix = "%Y%m%d.txt"
fileshandle.setLevel(logging.INFO)
formatter = logging.Formatter(fmt_str)
fileshandle.setFormatter(formatter)
logger.addHandler(fileshandle)


if __name__ == '__main__':
    logger.debug('debug')
    logger.info('info')
    logger.warn('warn')
    logger.error('error')
    logger.critical('critical')
