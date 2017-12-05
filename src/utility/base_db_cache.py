#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import sqlite3
import threading
sys.path.insert(0, '..')
from utility.singleton import Singleton
from utility.common import Common
from utility.log import Log

__author__ = 'Lin Xiaobin'

__all__ = ['BaseDBCache']


class BaseDBCache(object, metaclass=Singleton):

    def __init__(self, dbPath):
        self._dbLock = threading.Lock()
        self._dbPath = dbPath
        self._create_direcotry()
        self._connection = sqlite3.connect(self._dbPath, check_same_thread=False)

    def backup(self):
        Common.replace_file(self._dbPath, self._dbPath + '.bak')

    def commit(self):
        self._execute_sql(';', isQueury=False, commit=True)

    def is_table_contains_column(self, table, column):
        if table and column:
            sql = self._query_sql('select sql from sqlite_master where type="table" and tbl_name="%s"' % (table))
            if sql:
                sql = sql[0][0]
                regular = r',?\s+[\'"]?' + column + r'[\'"]?\s+'
                r = Common.rex_search(regular, sql, flags=re.M)
                if r is not None:
                    return True

        return False

    def table_add_column(self, table, column, columntype, default=None):
        if not table or not column or not columntype:
            return

        if self.is_table_contains_column(table, column):
            return

        cmd = 'ALTER TABLE %s ADD COLUMN %s %s' % (table, column, columntype)
        self._update_sql(cmd, commit=False)
        if default is not None:
            cmd = 'update %s set %s=%s where %s is null' % (table, column, default, column)
            # print(cmd)
            self._update_sql(cmd, commit=False)
        self.commit()

    def vacuum(self):
        self._execute_sql('vacuum', isQueury=False, commit=True)

    def _create_direcotry(self):
        if self._dbPath:
            directory = os.path.abspath(self._dbPath)
            directory = os.path.split(directory)[0]
            Common.create_dir(directory)
        else:
            Log.error('empty db path')

    def _query_sql(self, cmd, commit=False):
        return self._execute_sql(cmd, isQueury=True, commit=commit)

    def _update_sql(self, cmd, commit=True):
        return self._execute_sql(cmd, isQueury=False, commit=commit)

    def _execute_sql(self, cmd, isQueury=True, commit=True):
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
            Log.error('db except: ', e)
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
