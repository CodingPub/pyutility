#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image
from utility.common import *

__author__ = 'Lin Xiaobin'

__all__ = ['scaleImageWdith']


def scaleImageWdith(srcPath, dstPath, newWidth):
    if not isfile(srcPath):
        return

    remove(dstPath)

    img = Image.open(srcPath)
    size = img.size
    print(size)

    newHeight = newWidth * size[1] / size[0]
    img.resize((newWidth, int(newHeight)), Image.ANTIALIAS).save(dstPath)


if __name__ == '__main__':
    srcPath = '/Users/linxiaobin/Developer/python/KeyboardThemeTool/exports/black/smock/preview.png'
    dstPath = '/Users/linxiaobin/Developer/python/KeyboardThemeTool/exports/black/smock/thumbnail.png'
    scaleImageWdith(srcPath, dstPath, 480)
