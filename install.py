#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utility import *

cmd = 'python setup.py install --record install.txt'
systemCmd(cmd, directory=cmddir())
