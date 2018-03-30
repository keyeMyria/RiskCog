"""
Corret jump point error.

Usage:
    python jperr_check.py [-v] YOUR_PATH NEW_PATH a

Return:
    Write corrected sequence.

Args:
    -v: show details on every correction
    YOUR_PAHT: file path to be checked
    NEW_PATH: see 'Return'
    a: constant, see 'Error Defination Document'

Author:
    Qiang Liu
"""

import sys
import os
import numpy as np


def jump_point_correction(a, ratio, verbose=False):
    dict_ = [
        'acceleration x',
        'acceleration y',
        'acceleration z',
        'gyroscope x',
        'gyroscope y',
        'gyroscope z',
        'gravity x',
        'gravity y',
        'gravity z',
    ]

    if verbose:
        print 'sensor axis position last original -> corrcted next'

    for index, sequ in enumerate(a.T):
        # acceleration 0, 1, 2
        # gyrocope 3, 4, 5
        # gravity 6, 7, 8
        # UPDATE HERE
        # if index == 3 or index == 4 or index == 5:
        #    continue
        for i in range(0, len(sequ)-1):
            if i == 0:
                continue
            left_diff = sequ[i] - sequ[i-1]
            right_diff = sequ[i+1] - sequ[i]

            if left_diff * right_diff < 0 and abs(left_diff) >= ratio * 9.8 and abs(right_diff) >= ratio * 9.8:
                old = sequ[i]
                sequ[i] = 0.5 * (sequ[i-1] + sequ[i+1])
                if verbose:
                    print dict_[index], i, sequ[i-1], old, '->', sequ[i], sequ[i+1]
    return a


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python jperr_check.py [-v] YOUR_PATH NEW_PATH a')
        exit(-1)

    # get parameters
    verbose = False
    if sys.argv[1].startswith('-'):
        option = sys.argv[1][1:]
        if option == 'v':
            verbose = True

    a_ = float(sys.argv[-1])
    path = sys.argv[-3]
    new_path = sys.argv[-2]

    raw_data = np.loadtxt(path).reshape(-1, 9)
    corrected_data = jump_point_correction(raw_data, a_, verbose=verbose).reshape(-1, 1)
    np.savetxt(new_path, corrected_data, fmt='%.10f')
