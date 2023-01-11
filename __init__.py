import os, sys

parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


sys.path.append(parent)

import setup as s

s.config_labels()