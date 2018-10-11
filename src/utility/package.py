#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, '..')
from utility.common import Common
from utility.log import Log

__author__ = 'Lin Xiaobin'

__all__ = ['Package']


class Package(object):
    """docstring for Package"""

    def __init__(self, files, distdir):
        super(Package, self).__init__()
        self.files = files
        self.distdir = distdir
        Common.create_dir(distdir)

        Log.debug('packages: %s' % files)
        Log.debug('distdir: %s' % distdir)

    def run(self):
        self._cleanBuildInfo()
        self._buildPys()
        self._cleanBuildInfo()

    def _buildPys(self):
        for path in self.files:
            f1 = os.path.splitext(Common.join_paths(self.distdir, Common.split_path(path)[-1]))[0]
            f2 = f1 + '.exe'
            Common.remove(f1)
            Common.remove(f2)

            cmd = 'pyinstaller %s -F --distpath %s' % (path, self.distdir)
            Common.system_cmd(cmd, directory=Common.split_path(path)[0])

    def _cleanBuildInfo(self):
        for path in self.files:
            directory = Common.split_path(path)[0]

            Common.remove(Common.join_paths(directory, '__pycache__'))
            Common.remove(Common.join_paths(directory, 'build'))

            specs = [x for x in os.listdir(directory)
                     if os.path.isfile(x)
                     and os.path.splitext(x)[1] == '.spec']
            for x in specs:
                path = Common.join_paths(directory, x)
                Common.remove(path)


def main():
    files = ['Log.py', 'singleton.py']
    directory = Common.get_cmd_dir()
    paths = [Common.join_paths(directory, x) for x in files]
    distdir = Common.join_paths(Common.split_path(directory)[0], 'dist')
    Package(paths, distdir).run()


if __name__ == '__main__':
    main()
