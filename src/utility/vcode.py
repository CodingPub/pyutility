#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytesseract
from PIL import Image


__all__ = ['vcode']


def initTable(threshold=140):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    return table


def vcode(image, cropbox, threshold=175):
    rep = {'O': '0',
           'I': '1',
           'L': '1',
           'Z': '2',
           'S': '8',
           '£': '8'}

    im = image.crop(cropbox)
    im = im.convert('L')
    im = im.point(initTable(threshold=threshold), '1')

    text = pytesseract.image_to_string(im, config='-psm 7')
    text = text.strip(' [];-\',')
    text = text.upper()
    for c in ',.\'"‘?_ ~:“’':
        text = text.replace(c, '')
    for r in rep:
        text = text.replace(r, rep[r])

    return text
