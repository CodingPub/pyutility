import sys
import os
path = os.path.split(os.path.dirname(__file__))[0]
sys.path.insert(0, path)
print('sys.path:', sys.path)