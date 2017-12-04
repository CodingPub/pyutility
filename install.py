#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
path = os.path.join(os.path.dirname(__file__), 'src')
# path = os.path.join(path, 'utility')
sys.path.insert(0, path)
from utility.common import Common


directory = Common.get_cmd_dir()

# cmd = 'git pull --all'
# systemCmd(cmd, directory=directory)

cmd = 'python setup.py install --record install.txt'

Common.system_cmd(cmd, directory=directory)
