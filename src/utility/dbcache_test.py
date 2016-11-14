import unittest
import tempfile
from utility import *
from dbcache import *


class TestDBCache(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testInit(self):
        path = joinPaths(tempfile.gettempdir(), 'test.db')
        self.assertEqual(DBCache(path), DBCache(), msg='initial db error')

    def testCreateTable(self):
        pass


if __name__ == '__main__':
    unittest.main()
