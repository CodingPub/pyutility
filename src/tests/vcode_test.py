import unittest
import os
from PIL import Image
from utility import Common
from utility.vcode import *


def run(threshold):
    dir_path = Common.join_paths(Common.get_cmd_dir(), 'codes')
    files = [x for x in Common.list_dir(dir_path) if not x.startswith('.')]
    rightCount = 0
    for x in files:
        # print(x)+
        img_path = Common.join_paths(dir_path, x)
        print(img_path)
        im = Image.open(img_path)
        box = (5, 5, 43, 19)
        text = vcode(im, box, threshold=threshold)

        real = os.path.splitext(x)[0]
        print("real: %s, cal: %s", real, text)
        if text == real:
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
    # unittest.main()

    run(175)

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
