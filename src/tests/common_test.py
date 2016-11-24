import addpath
import unittest
import os
import tempfile
from utility.common import *


class TestCommon(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDebug(self):
        msg = 'DEBUG flag error'
        self.assertFalse(isDebug(), msg=msg)
        setDebug(True)
        self.assertTrue(isDebug(), msg=msg)

    def testCmdDirectory(self):
        path = cmddir()
        self.assertIsNotNone(path, msg='get cmd directory error')

    def testlistdir(self):
        arr = listdir('.', extRex='.py')
        msg = 'list directory error'
        self.assertIsNotNone(arr, msg=msg)
        self.assertGreater(len(arr), 0, msg=msg)

    def testDirectoryOpt(self):
        directory = joinPaths(tempfile.gettempdir(), 'aa', 'b')
        directory = os.path.abspath(directory)
        # print(directory)
        createdir(directory)
        self.assertTrue(os.path.isdir(directory), msg='create directory error')

        path = joinPaths(directory, 'test.txt')
        writefile(path, 'test str', encoding='utf-8')
        self.assertTrue(os.path.isfile(path), msg='write str error')

        remove(path)
        self.assertFalse(os.path.isfile(path), msg='remove file error')

        directory = os.path.split(directory)[0]
        remove(directory)
        self.assertFalse(os.path.isdir(directory), msg='remove dir error')

    def testMultRun(self):
        resultSet = set()

        def foo(arr, idx):
            if not arr or idx < 0 or idx >= len(arr):
                return False

            resultSet.add(arr[idx])
            return True

        arr = list(range(100))
        s = set(arr)
        multiRun(foo, arr, 2, 'Start...', 'Finish...')
        self.assertEqual(s, resultSet, msg='multi run error')


if __name__ == '__main__':
    unittest.main()
