import os
import sys
import json

sys.path.insert(0, '/home/nelley/casperPractice/PTT/mongoScript')
from trie import *


if __name__ == '__main__':
    restore_data = deserialize_all()
    get_all_in_depth(restore_data)


