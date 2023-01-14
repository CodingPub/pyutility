#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')
from utility.common import Common
from utility.log import Log

__all__ = ['HeaderUtil']

class HeaderUtil(object):

    @classmethod
    def get_header(cls, filename):
        head_path = Common.join_paths(Common.get_cmd_dir(), filename)
        head_arr = Common.read_file(head_path).split('\n')
        head_dict = {}
        for x in head_arr:
            kv = x.split(':')
            key = kv[0]
            if key:
                value = ':'.join(kv[1:])
                head_dict[key] = value
            # Log.debug('%s %s %s', key, ' ===> ', value)
        return head_dict

def main():
    src_path = '/Users/linxiaobin/develop/python/py_subject_monitor/net/xue_qiu_header.txt'
    headers = HeaderUtil.get_header(src_path)
    Log.debug('%s', headers)


if __name__ == '__main__':
    main()
