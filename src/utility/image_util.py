#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PIL import Image

sys.path.insert(0, '.')
from utility.common import Common

__author__ = 'Lin Xiaobin'

__all__ = ['ImageUtil']


class ImageUtil(object):

    @classmethod
    def scale_image_file(cls, src, dst, newWidth):
        if not Common.isfile(src):
            return

        Common.remove(dst)

        img = Image.open(src)
        size = img.size
        print(size)

        newHeight = newWidth * size[1] / size[0]
        img.resize((newWidth, int(newHeight)), Image.ANTIALIAS).save(dst)


def main():
    src_path = '/Users/linxiaobin/Developer/python/KeyboardThemeTool/exports/black/smock/preview.png'
    dst_path = '/Users/linxiaobin/Developer/python/KeyboardThemeTool/exports/black/smock/thumbnail.png'
    ImageUtil.scale_image_file(src_path, dst_path, 480)


if __name__ == '__main__':
    main()
