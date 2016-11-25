#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utility import *

directory = cmddir()

if systemCmd('git --version'):
    cmd = 'git pull --all'
    systemCmd(cmd, directory=directory)

cmd = 'python setup.py install --record install.txt'
systemCmd(cmd, directory=directory)
