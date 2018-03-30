"""
Zero error check tool.

Usage:
    python zrerr.py YOUR_PATH

Return:
    Return zero error mark matrix that is length of samples by asex.
    If a zero error appears, the mark will be is 1 , or is 0.
    For example:
    return = [[0 0 0]
              [0 1 0]
              [0 0 0]
              ...
              [0 1 0]]
    means there are two zero errors on sensor 2.

Args:
    YOUR_PAHT: file path to be checked

Author:
    Qiang Liu
"""


import numpy as np
import sys

def zrerr_check(a):
    a = a.reshape(-1, 3)

    eps = 0.0000000001
    mark = []
    for group in a:
        if abs(group[0]) < eps and abs(group[1]) < eps and abs(group[2]) < eps:
            mark.append(1)
        else:
            mark.append(0)
    mark = np.array(mark).reshape(-1, 3)

    return mark

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: python zrerr.py YOUR_PATH'
        exit(-1)
    path = sys.argv[1]

    raw_data = np.loadtxt(path).reshape(-1, 9)
    mark = zrerr_check(raw_data)
    print mark

    # you can do some statistics in your code like below
    # mark_sum = mark.sum(axis=0)
    # print raw_data.shape[0], mark_sum, path
