"""
Normalization.

Usage:
    Usage: python normalization.py [-a] TABLE ROOT TARGET

Return:
    Normalization. Store like TARGET/your_imei/file_1.

Args:
    ROOT     The root directory which contains the
             sensor data and ensure that every file is
             directly beneath the directory named by imei,
             such as ROOT/your_imei/file_1.
    TARGET   Target dir after normalization.
    TABLE    Dir that stores the extrema files.
    -a       Don't remove gravity from acceleration.
    -v       Show process of normalization.
    -g       Globle normalization.

Author:
    This script is originally written by Zi Lin and updated by Qiang Liu.
"""

import os
import sys
import numpy as np

def createDir(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)


def normalization(a, min_, max_, rmgrfacc=False):
    # remove gravity from acceleration
    if rmgrfacc:
        acceleration = a[:, 0:3] - a[:, 6:9]
        a = np.hstack((acceleration, raw_data[:, 3:9]))

    return 2.0 * (a - min_) / (max_ - min_) - 1.0


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Usage: python normalization [-a] [-v] [-g] TABLE ROOT TARGET'
        print '  ROOT     The root directory which contains the \n' \
              '           sensor data and ensure that every file is \n' \
              '           directly beneath the directory named by imei, \n'\
              '           such as ROOT/your_imei/file_1.'
        print '  TARGET   Target dir after nomalization.'
        print '  TABLE    Dir that stores the extrema files.'
        exit(-1)

    # same as usual
    table = sys.argv[-3]
    root = sys.argv[-2]
    target = sys.argv[-1]
    rmgrfacc = True # remove_gravity_from_acceleration
    g_normalization = False
    verbose = False

    for index, argv in enumerate(sys.argv):
        if argv == '-a':
            rmgrfacc = False
        if argv == '-v':
            verbose = True
        if argv == '-g':
            g_normalization = True

    createDir(target)
    imeis = os.listdir(root)
    for imei_index, imei in enumerate(imeis):
        # get files under root/imei
        user_dir = os.path.join(root, imei)
        if not os.path.isdir(user_dir):
            continue
        file_list = os.listdir(user_dir)

        createDir(os.path.join(target, imei))
        for file_name in file_list:
            raw_data = np.loadtxt(os.path.join(root, imei, file_name))
            raw_data = np.reshape(raw_data, (-1, 9))

            # unique code begin
            if g_normalization:
                extrema = np.loadtxt(os.path.join(table, 'globle'))
            else:
                extrema = np.loadtxt(os.path.join(table, imei))
            raw_data = normalization(raw_data, extrema[:9], extrema[9:], rmgrfacc=rmgrfacc).reshape(-1, 1)
            np.savetxt(os.path.join(target, imei, file_name), raw_data, fmt='%.10f')
            # unique code end
        if verbose:
            print imei_index, imei, 'done'
