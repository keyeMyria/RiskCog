"""
Gen sliding windows in given length.

Usage:
    Usage: python window_sliding [-l interval_len] [-ol overlap] [-v] [-f file_name] [-i imei] ROOT TARGET

Return:
    Gen sliding windows in given length with structure like
    TARGET/your_imei/file_1

Args:
    ROOT     The root directory which contains the
             sensor data and ensure that every file is
             directly beneath the directory named by imei,
             such as ROOT/your_imei/file_1.
    TARGET   Target dir of sliding windows.
    -l       Interval length of sliding window.
    -ol      Overlap of sliding window.
    -i       The imei you want to format directly.
    -f       File name of raw data you want to format directly. But you have to set -i first.

Author:
    This script is originally written by Zi Lin and updated by Qiang Liu.
"""

import os
import sys
import numpy


def createDir(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)


if __name__ == '__main__':
    # root = '/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/train'
    if len(sys.argv) == 1:
        print 'Usage: python window_sliding [-l interval_len] [-ol overlap] [-v]' \
              '[-f file_name] [-i imei] ROOT TARGET'
        print '  ROOT     The root directory which contains the \n' \
              '           sensor data and ensure that every file is \n' \
              '           directly beneath the directory named by imei, \n'\
              '           such as ROOT/your_imei/file_1.'
        print '  TARGET   Target dir of slding windows.'
        exit(-1)

    # save as usual
    root = sys.argv[-2]
    target = sys.argv[-1]
    interval_Len = 75
    overlap = 0.5
    verbose = False
    imei_specific = None
    file_specific = None

    for index, argv in enumerate(sys.argv):
        if argv == '-l':
            interval_Len = int(sys.argv[index+1])
        if argv == '-ol':
            overlap = float(sys.argv[index+1])
        if argv == '-v':
            verbose = True
        if argv == '-i':
            imei_specific = sys.argv[index+1]
        if argv == '-f':
            file_specific = sys.argv[index+1]

    createDir(target)
    imeis = os.listdir(root)
    for imei_index, imei in enumerate(imeis):
        if imei_specific and imei != imei_specific:
            continue

        user_dir = os.path.join(root, imei)
        if file_specific and imei_specific:
            file_list= [file_specific]
        else:
            file_list = os.listdir(user_dir)

        for file_name in file_list:
            # get raw data whose path is root/imei/file_name
            # raw_data is an array N/9 by 9
            raw_data = numpy.loadtxt(os.path.join(root, imei, file_name))
            raw_data = numpy.reshape(raw_data, (-1, 9))

            # unique code begin
            # split by sliding window
            tmp_dir = os.path.join(target, imei)
            createDir(tmp_dir)

            sts = numpy.arange(0, raw_data.shape[0] - 1, interval_Len * overlap, dtype='int16')
            # print sts
            for count, st in enumerate(sts):
                if st + interval_Len >= raw_data.shape[0]:
                    # tmp = raw_data[st:, :].reshape(-1, 1)
                    continue
                else:
                    tmp = raw_data[st:st + interval_Len, :].reshape(-1, 1)
                numpy.savetxt('{0}/{1}_part_{2}'.format(tmp_dir, file_name, count), tmp, fmt='%.10f')
            # unique code end
        if verbose:
            print imei_index, imei, 'done'
