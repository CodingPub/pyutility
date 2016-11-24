#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import threading
from utility import *

__author__ = 'Lin Xiaobin'

__all__ = ['DBCache']


class DBCache(object, metaclass=Singleton):

    def __init__(self, dbPath):
        self._dbLock = threading.Lock()
        self._dbPath = dbPath
        self._createDirecotry()
        self._connection = sqlite3.connect(self._dbPath, check_same_thread=False)

    def backup(self):
        replacefile(self._dbPath, self._dbPath + '.bak')

    def commit(self):
        self._executeSQL(';', isQueury=False, commit=True)

    def vacuum(self):
        self._executeSQL('vacuum', isQueury=False, commit=True)

    def _createDirecotry(self):
        if self._dbPath:
            directory = os.path.abspath(self._dbPath)
            directory = os.path.split(directory)[0]
            createdir(directory)
        else:
            logger.error('empty db path')

    def _querySQL(self, cmd, commit=False):
        return self._executeSQL(cmd, isQueury=True, commit=commit)

    def _updateSQL(self, cmd, commit=True):
        return self._executeSQL(cmd, isQueury=False, commit=commit)

    def _executeSQL(self, cmd, isQueury=True, commit=True):
        values = []
        rowCount = 0
        self._dbLock.acquire()
        try:
            con = self._connection
            cursor = con.cursor()
            cursor.execute(cmd)
            values = cursor.fetchall()
            rowCount = cursor.rowcount
            if not isQueury and commit:
                con.commit()
        except Exception as e:
            print('except: ', e)
            # raise e
        finally:
            cursor.close()
            self._dbLock.release()

        if isQueury:
            return values
        else:
            return rowCount


if __name__ == '__main__':
    pass
