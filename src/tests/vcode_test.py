import addpath
import unittest
import os
from PIL import Image
from utility import *
from utility.vcode import *


def run(threshold):
    files = [x for x in listdir('codes') if not x.startswith('.')]
    rightCount = 0
    for x in files:
        # print(x)
        im = Image.open(joinPaths('codes', x))
        box = (5, 5, 43, 19)
        text = vcode(im, box, threshold=threshold)

        if text == os.path.splitext(x)[0]:
            rightCount += 1
    return rightCount


class TestVcode(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testVcode(self):
        right = run(175)
        print(right)
        # self.assertGreaterEqual(right, 26, '验证准确性不足')


if __name__ == '__main__':
    unittest.main()

    # m = 0
    # mt = 0
    # for x in range(30):
    #     threshold = 160 + x
    #     right = run(threshold)
    #     print('threshold:', threshold, 'right:', right)
    #     if right > m:
    #         m = right
    #         mt = x
    # print('max:', mt, m)
