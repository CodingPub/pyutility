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

        def foo(arr, idx, args):
            print(args)
            resultSet.add(arr[idx])

        arr = list(range(10))
        s = set(arr)
        multiRun(foo, arr, 2, 'Start...', 'Finish...', args='test')
        self.assertEqual(s, resultSet, msg='multi run error')

        def foo2(idx, args):
            print(idx, args)
            if idx < 9:
                return True
            else:
                return False
        multiRun(foo2, None, 2, 'Start...', 'Finish...', args='test')


if __name__ == '__main__':
    unittest.main()
