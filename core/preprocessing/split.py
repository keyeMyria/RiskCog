"""
Split file by a mark matrix.

Usage:
    Usage: python split.py [-z] [-v] YOUR_PATH

Return:
    Split file into pieces named like YOUR_PATH_(INDEX) by a mark matrix.

Args:
    -z: split file by a mark matrix that is from zrerr, required
    YOUR_PAHT: file path to be split

Author:
    Qiang Liu
"""

import numpy as np
import sys
from zrerr_check import zrerr_check

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Usage: python split.py [-z] [-v] YOUR_PATH'
        exit(-1)
    path = sys.argv[-1]

    zrerr = False
    verbose = False
    for index, argv in enumerate(sys.argv):
        if argv == '-z':
            zrerr = True
        if argv == '-v':
            verbose = True

    if zrerr:
        raw_data = np.loadtxt(path).reshape(-1, 9)
        mark = zrerr_check(raw_data)
        position = np.zeros(raw_data.shape[0])
        for m in mark.T:
            position += m

        position =  np.where(position > 0)[0].tolist()
        if verbose:
            print 'position of zrerr:', position
        position.append(raw_data.shape[0])

        for i in range(len(position)):
            end = position[i]
            if i == 0:
                start = 0
            else:
                start = position[i-1]

            path_o = '{0}_{1}'.format(path, i)
            if end - start > 1:
                np.savetxt(path_o, raw_data[start+1:end, :])
                if verbose:
                    print '({0}, {1}), save to {2}'.format(start, end, path_o)
