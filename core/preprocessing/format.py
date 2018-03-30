# -*- coding: UTF-8 -*-
"""
With this script you can change the format of the sensor data uploaded
to the format of which LSTM requires.

Usage:
    Usage: python format [-h] [-l interval_len] [-ol overlap] [-a]
           [-n valid_file_number] [-t] ROOT TARGET

Return:
    Change the format of the sensor data uploaded to the format of which LSTM
    requires under TARGET.
larger than THRESHOLD

Args:
    ROOT     Update the root directory which contains the
             sensor data and ensure that every file is
             directly beneath the directory named by imei,
             such as ROOT/your_imei/file_1.
    TARGET   Target dir of data set.
    -h       Print usage and this help message and exit.
    -l       Interval length of sliding window.
    -ol      Overlap of sliding window.
    -a       Don't remove gravity from acceleration.
    -n       Least number of VALID files.'
    -np      Specify the number of files you want to pick up. If not set,
             find the least one. If set, np can not be
             lower than n
    -t       Don't remove tmp dir.

Author:
    This script is originally written by Zi Lin and updated by Qiang Liu.
"""

import os
import sys
import numpy
import random
from sklearn.model_selection import train_test_split


# 该函数将某用户的所有文件数据导入对应最终文件中
def dataLoad(filePath, fileList, fileType, count, newPath):
    paraName = ['total_acc_x_', 'total_acc_y_', 'total_acc_z_', 'body_gyro_x_', 'body_gyro_y_', 'body_gyro_z_',
                'body_acc_x_', 'body_acc_y_', 'body_acc_z_']

    for myFile in fileList:
        with open(os.path.join(newPath, fileType, 'y_' + fileType + '.txt'), 'a+') as f:
            f.write(str(count) + '\n')

        myData = numpy.loadtxt(os.path.join(filePath, myFile), dtype='str').reshape(-1, 9).T
        for i, data in enumerate(myData):
            with open(os.path.join(newPath, fileType, paraName[i] + fileType + '.txt'), 'a+') as f:
                f.write(' '.join(data))
                f.write('\n')
                f.close()

    return None


def get_number_to_pick_up(root, number=None, lowest=None):
    N = []
    if number is None:
        for root_, dir_, file_ in os.walk(root):
            if len(file_) < lowest:
                continue
            else:
                N.append(len(file_))
        if len(N) == 0:
            number = lowest
        else:
            number = min(N)
    return number


def createDir(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)


if __name__ == '__main__':
    # root = '/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/train_set'
    if len(sys.argv) == 1:
        print 'Usage: python format [-h] [-l interval_len] [-ol overlap] [-a] ' \
              '[-n valid_file_number] [-np number] [-t] ROOT TARGET'
        print '  ROOT     Update the root directory which contains the \n' \
              '           sensor data and ensure that every file is \n' \
              '           directly beneath the directory named by imei, \n'\
              '           such as ROOT/your_imei/file_1.'
        print '  TARGET   Target dir of data set.'
        exit(-1)

    root = sys.argv[-2]
    interval_Len = 75
    overlap = 0.5
    validFileNumber = 100
    number_to_pick_up = None
    rmgrfacc = True # remove_gravity_from_acceleration
    remove_tmp = True
    tmp_root = './splitData_tmp'
    result_root = sys.argv[-1]
    normalization = True

    # check parameters
    for index, argv in enumerate(sys.argv):
        if argv == '-h':
            print 'Usage: python format [-h] [-l interval_len] [-ol overlap] [-a]' \
                  '[-n valid_file_number] [-np number] [-t] ROOT'
            print '  ROOT     Update the root directory which contains the\n' \
                  '           sensor data and ensure that every file is\n' \
                  '           directly beneath the directory named by imei,\n' \
                  '           such as ROOT/your_imei/file_1.'
            print '  TARGET   Target dir of data set.'
            print '  -------  Options -------'
            print '  -h       Print usage and this help message and exit.'
            print '  -l       Interval length of sliding window.'
            print '  -ol      Overlap of sliding window.'
            print '  -a       Don\'t remove gravity from acceleration.'
            print '  -n       Least number of VALID files.'
            print '  -np      Specify the number of files you want to pick up. If not set,\n' \
                  '           find the least one. If set, np can not be\n' \
                  '           lower than n'
            print '  -t       Don\'t remove tmp dir.'
            exit(-1)
        if argv == '-l':
            interval_Len = int(sys.argv[index+1])
        if argv == '-ol':
            overlap = float(sys.argv[index+1])
        if argv == '-a':
            rmgrfacc = False
        if argv == '-n':
            validFileNumber = int(sys.argv[index+1])
        if argv == '-np':
            number_to_pick_up = int(sys.argv[index+1])
        if argv == '-t':
            remove_tmp = False

    if number_to_pick_up is not None:
        if number_to_pick_up < validFileNumber:
            raise ValueError('-np {0} is lower than -n ' \
                             '{1}'.format(number_to_pick_up, validFileNumber))
    # check parameters done

    os.system('rm -rf %s' % result_root)

    print('Window sliding starts ...')

    print '-------Config-------\n-interval length {0}\n' \
          '-overlap {3}\n' \
          '-valid file number {2}\n'.format(interval_Len, normalization, validFileNumber,
                                 overlap, tmp_root, result_root, remove_tmp)
    # if number_to_pick_up is not None:
    #     print '-number to pick up {0}\n'.format(number_to_pick_up)

    imeis = os.listdir(root)
    for imei_index, imei in enumerate(imeis):

        # get files under root/imei
        user_dir = os.path.join(root, imei)
        if not os.path.isdir(user_dir):
            continue
        file_list = os.listdir(user_dir)

        min_ = None
        max_ = None

        for file_name in file_list:
            # get raw data whose path is root/imei/file_name
            # raw_data is an array N/9 by 9
            raw_data = numpy.loadtxt(os.path.join(root, imei, file_name))
            raw_data = numpy.reshape(raw_data, (-1, 9))

            # remove gravity from acceleration
            if rmgrfacc:
                acceleration = raw_data[:, 0:3] - raw_data[:, 6:9]
                raw_data = numpy.hstack((acceleration, raw_data[:, 3:9]))

            # normalization
            if normalization:
                # get min and max of each axis of every sensor
                # TODO MAY SET UP A THRESHOLD
                min_t = raw_data.min(axis=0)
                max_t = raw_data.max(axis=0)
                if min_ is None:
                    min_ = min_t
                else:
                    min_[numpy.where(min_ > min_t)] = min_t[numpy.where(min_ > min_t)]
                if max_ is None:
                    max_ = max_t
                else:
                    max_[numpy.where(max_ < max_t)] = max_t[numpy.where(max_ < max_t)]
                raw_data = 2.0 * (raw_data - min_) / (max_ - min_) - 1.0

            # split by sliding window
            tmp_dir = os.path.join(tmp_root, imei)
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

        print '{0}, {1}, OK'.format(imei_index, imei)

    print 'Window sliding overs.\n'

    print 'Formating starts ...'

    number_to_pick_up = get_number_to_pick_up(tmp_root, number_to_pick_up,
                                              lowest=validFileNumber)
    print '\npick up {0} files'.format(number_to_pick_up)

    count = 0
    createDir(os.path.join(result_root, 'train'))
    createDir(os.path.join(result_root, 'test'))
    for imei in imeis:
        user_dir = os.path.join(tmp_root, imei)
        file_list = os.listdir(user_dir)

        origin_len = len(file_list)
        if len(file_list) < validFileNumber or len(file_list) < number_to_pick_up:
            # count = count + 1
            print '-', '  ', imei, '  total file number: ', str(len(file_list)), '  NOT ENOUGH DISCARD'
            continue
        else:
            # pick up
            file_list = random.sample(file_list, number_to_pick_up)

        count = count + 1

        train_files, test_files = train_test_split(file_list, test_size=0.2)
        dataLoad(user_dir, train_files, 'train', count, result_root)
        dataLoad(user_dir, test_files, 'test', count, result_root)

        print str(count), '  ', imei, '  total file number: ', str(origin_len), '->',  str(len(file_list)), '  OK'

    if remove_tmp:
        os.system('rm -rf %s' % tmp_root)

    print 'Formating over.\n'
