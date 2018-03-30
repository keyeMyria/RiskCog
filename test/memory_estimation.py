#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy as np
import sys
from guppy import hpy
from memory_profiler import profile

@profile(precision=4)
def main(filepath):
    # data = np.loadtxt(filepath, dtype=np.float32)
    with open(filepath) as f:
        data = [float(line) for line in f.readlines()]

if __name__ == '__main__':
    main('./test_data/100K')
    # main('./test_data/500K')
    # main('./test_data/1M')
    # main('./test_data/5M')
    # main('./test_data/10M')
    # main('./test_data/50M')
    # main('./test_data/100M')
    # main(sys.argv[-1])



