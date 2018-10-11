#!/usr/bin/env python
# encoding: utf-8
# filename: gzip.py
# author: tao_627@aliyun.com
# date: 2015-06-30

import gzip
import binascii
from io import BytesIO


__all__ = ['GZip']


class GZip(object):

    @classmethod
    def compress(cls, raw_data):
        buf = BytesIO()
        f = gzip.GzipFile(mode='wb', fileobj=buf)
        try:
            f.write(raw_data)
        finally:
            f.close()
        return buf.getvalue()

    @classmethod
    def uncompress(cls, c_data):
        buf = BytesIO(c_data)
        f = gzip.GzipFile(mode='rb', fileobj=buf)
        try:
            rdata = f.read()
        finally:
            f.close()
        return rdata

    @classmethod
    def compress_file(cls, fn_in, fn_out):
        f_in = open(fn_in, 'rb')
        f_out = gzip.open(fn_out, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()

    @classmethod
    def uncompress_file(cls, fn_in, fn_out):
        f_in = gzip.open(fn_in, 'rb')
        f_out = open(fn_out, 'wb')
        file_content = f_in.read()
        f_out.write(file_content)
        f_out.close()
        f_in.close()


if __name__ == '__main__':
    in_data = bytes('hello, world!', 'utf-8')
    print(in_data)
    out_data = GZip.compress(in_data)
    print(binascii.hexlify(out_data))

    r_data = GZip.uncompress(out_data)
    print(r_data)
