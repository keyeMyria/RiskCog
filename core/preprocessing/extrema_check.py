"""
extrema check

Usage:
    python extrema_check.py [-v] TABLE ROOT TARGET 

Return:
    Each user will have a file that stores its extrema.

Args:
    ROOT     The root directory which contains the
             sensor data and ensure that every file is
             directly beneath the directory named by imei,
             such as ROOT/your_imei/file_1.
    TARGET   Target directory.
    TABLE    Dir that stores the extrema files.
    -v       Show extrema of every user.
    -g       Globel normalization.

Author:
    This script is originally written by Zi Lin and updated by Qiang Liu.
"""
import numpy as np
import sys
import os


def createDir(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)


def extrema_check(a):
    return a.min(axis=0), a.max(axis=0)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Usage: python extrema_check.py [-v] [-g] TABLE ROOT TARGET'
        print '  ROOT     The root directory which contains the \n' \
              '           sensor data and ensure that every file is \n' \
              '           directly beneath the directory named by imei, \n'\
              '           such as ROOT/your_imei/file_1.'
        print '  TARGET   Target directory.'
        print '  TABLE    Dir that stores the extrema files.'
        exit(-1)

    # same as usual
    verbose = False
    g_normalization = False
    for argv in sys.argv:
        if argv.startswith('-v'):
            verbose = True
        if argv.startswith('-g'):
            g_normalization = True


    table = sys.argv[-3]
    root = sys.argv[-2]
    target = sys.argv[-1]

    createDir(target)
    imeis = os.listdir(root)
    for imei_index, imei in enumerate(imeis):
        # get files under root/imei
        user_dir = os.path.join(root, imei)
        if not os.path.isdir(user_dir):
            continue
        file_list = os.listdir(user_dir)

        if os.path.exists(os.path.join(table, imei)):
            min_ = np.loadtxt(os.path.join(table, imei))[:9]
            max_ = np.loadtxt(os.path.join(table, imei))[9:]
        else:
            min_ = None
            max_ = None

        for file_name in file_list:
            raw_data = np.loadtxt(os.path.join(root, imei, file_name)).reshape(-1, 9)
            # unique code begin
            min_t, max_t = extrema_check(raw_data)
            if min_ is None:
                min_ = min_t
            else:
                min_[np.where(min_ > min_t)] = min_t[np.where(min_ > min_t)]
            if max_ is None:
                max_ = max_t
            else:
                max_[np.where(max_ < max_t)] = max_t[np.where(max_ < max_t)]

        # check g_normalization
        if g_normalization and os.path.exists(os.path.join(table, 'globle')):
            extrema_old_min = np.loadtxt(os.path.join(table, 'globle'))[:9]
            extrema_old_max = np.loadtxt(os.path.join(table, 'globle'))[9:]

            min_[np.where(min_ > extrema_old_min)] = extrema_old_min[np.where(min_ > extrema_old_min)]
            max_[np.where(max_ < extrema_old_max)] = extrema_old_max[np.where(max_ < extrema_old_max)]
            # unique code end
        if verbose:
            print imei_index, imei
            print '-min:', min_.tolist()
            print '-max:', max_.tolist()
        if g_normalization:
            # print '-g set'
            np.savetxt(os.path.join(target, 'globle'), np.append(min_, max_), fmt='%.10f')
        else:
            np.savetxt(os.path.join(target, imei), np.append(min_, max_), fmt='%.10f')
