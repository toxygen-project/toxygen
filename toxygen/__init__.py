import os
import sys

path = os.path.dirname(os.path.realpath(__file__))  # curr dir

sys.path.insert(0, os.path.join(path, 'styles'))
sys.path.insert(0, os.path.join(path, 'plugins'))
sys.path.insert(0, path)
