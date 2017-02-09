#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
path = os.path.join(os.path.dirname(__file__), 'src')
# path = os.path.join(path, 'utility')
sys.path.insert(0, path)


from utility import *


directory = cmddir()

if systemCmd('git --version') == 0:
    cmd = 'git pull --all'
    systemCmd(cmd, directory=directory)

cmd = 'python setup.py install --record install.txt'
systemCmd(cmd, directory=directory)
