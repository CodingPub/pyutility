import addpath
import unittest
from utility import *

class TestSingleton(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDecorator(self):
        @singleton
        class ClassA(object):
            def __init__(self, arg1, t=None):
                # super(ClassA, self).__init__()
                self.arg1 = arg1
                self.t = t
                pass

        a = ClassA(12, t='a')
        b = ClassA()
        msg = '单例异常'
        self.assertEqual(a, b, msg=msg)
        self.assertEqual(a.arg1, b.arg1, msg=msg)
        self.assertEqual(a.t, b.t, msg=msg)

    def testMultiInherit(self):
        class ClassB(object, metaclass=Singleton):
            def __init__(self, arg1, t=None):
                super(ClassB, self).__init__()
                self.arg1 = arg1
                self.t = t

        a = ClassB(12, t='a')
        b = ClassB()
        msg = '单例异常'
        self.assertEqual(a, b, msg=msg)
        self.assertEqual(a.arg1, b.arg1, msg=msg)
        self.assertEqual(a.t, b.t, msg=msg)

        class ClassC(ClassB):
            def __init__(self):
                super(ClassC, self).__init__(123, t='bbb')

        c = ClassC()
        d = ClassC()
        self.assertEqual(id(c), id(d), msg=msg)
        self.assertEqual(c.arg1, d.arg1, msg=msg)
        self.assertEqual(c.t, d.t, msg=msg)


if __name__ == '__main__':
    unittest.main()
