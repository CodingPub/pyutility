#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
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

    def tableContainsColumn(self, table, column):
        if table and column:
            sql = self._querySQL('select sql from sqlite_master where type="table" and tbl_name="%s"' % (table))
            if sql and len(sql) > 0:
                sql = sql[0][0]
                regular = r',?\s+[\'"]?' + column + r'[\'"]?\s+'
                r = rexSearch(regular, sql, flags=re.M)
                if r is not None:
                    return True

        return False

    def tableAddColumn(self, table, column, columntype, default=None):
        if not table or not column or not columntype:
            return

        if self.tableContainsColumn(table, column):
            return

        cmd = 'ALTER TABLE %s ADD COLUMN %s %s' % (table, column, columntype)
        self._updateSQL(cmd, commit=False)
        if default:
            cmd = 'update %s set %s=%s where %s is null' % (table, column, default, column)
            # print(cmd)
            self._updateSQL(cmd, commit=False)
        self.commit()

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
            print('db except: ', e)
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
