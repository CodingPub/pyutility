#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utility import *
import os

__author__ = 'Lin Xiaobin'


class Package(object):
    """docstring for Package"""
    def __init__(self, files, distdir):
        super(Package, self).__init__()
        self.files = files
        self.distdir = distdir
        createdir(distdir)

        logger.debug('packages: %s' % files)
        logger.debug('distdir: %s' % distdir)

    def run(self):
        self.cleanBuildInfo()
        self.buildPys()
        self.cleanBuildInfo()

    def buildPys(self):
        for path in self.files:
            f1 = os.path.splitext(joinPaths(self.distdir, splitPath(path)[-1]))[0]
            f2 = f1 + '.ext'
            remove(f1)
            remove(f2)

            cmd = 'pyinstaller %s -F --distpath %s' % (path, self.distdir)
            systemCmd(cmd, directory=splitPath(path)[0])

    def cleanBuildInfo(self):
        for path in self.files:
            directory = splitPath(path)[0]

            remove(joinPaths(directory, '__pycache__'))
            remove(joinPaths(directory, 'build'))

            specs = [x for x in os.listdir(directory) if os.path.isfile(x) and os.path.splitext(x)[1] == '.spec']
            for x in specs:
                path = joinPaths(directory, x)
                remove(path)


if __name__ == '__main__':
    files = ['logger.py', 'singleton.py']
    directory = cmddir()
    paths = [joinPaths(directory, x) for x in files]
    distdir = joinPaths(splitPath(directory)[0], 'dist')
    Package(paths, distdir).run()
