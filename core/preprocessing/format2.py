"""
With this script you can change the format of the sensor data uploaded
to the format of which LSTM requires.

Usage:
    Usage: python format.py [-n valid_file_number] [-np number] [-p proportion]
    [-f file_name] [-i imei] [-one lable/imei] ROOT TARGET

Return:
    Change the format of the sensor data uploaded to the format of which LSTM
    requires under TARGET.

Args:
    ROOT     The root directory which contains the
             sensor data and ensure that every file is
             directly beneath the directory named by imei,
             such as ROOT/your_imei/file_1.
    TARGET   Target dir of data set.
    -n       Least number of VALID files.'
    -np      Specify the number of files you want to pick up. If not set,
             find the least one. If set, np can not be
             lower than n. If set 0, do not pick up.
    -v       Show process of format.
    -p       Proportion of train set.
    -i       The imei you want to format directly.
    -f       File name of raw data you want to format directly. But you have to set -i first.
    -one     The imei that you want to be the first one.

Author:
    This script is originally written by Zi Lin and updated by Qiang Liu.
"""

import os
import sys
import numpy
import random
from sklearn.model_selection import train_test_split


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
        print 'Usage: python format2.py ' \
              '[-n valid_file_number] [-np number] [-p proportion] [-f file_name] [-i imei] [-one lable/imei] ROOT TARGET'
        print '  ROOT     Update the root directory which contains the \n' \
              '           sensor data and ensure that every file is \n' \
              '           directly beneath the directory named by imei, \n'\
              '           such as ROOT/your_imei/file_1.'
        print '  TARGET   Target dir of data set.'
        exit(-1)

    # save as usual
    root = sys.argv[-2]
    validFileNumber = 575
    number_to_pick_up = None
    target = sys.argv[-1]
    verbose = False
    proportion = 0.8
    file_specific = None
    imei_specific = None
    imei_first = None

    for index, argv in enumerate(sys.argv):
        if argv == '-n':
            validFileNumber = int(sys.argv[index+1])
        if argv == '-np':
            number_to_pick_up = int(sys.argv[index+1])
        if argv == '-v':
            verbose = True
        if argv == '-p':
            proportion = float(sys.argv[index+1])
        if argv == '-i':
            imei_specific = sys.argv[index+1]
        if argv == '-f':
            file_specific = sys.argv[index+1]
        if argv =='-one':
            # if -i set, imei_first will be the label of imei_specific
            # if -i not set, imei_first will be the first one.
            imei_first = sys.argv[index+1]

    if number_to_pick_up is not None:
        if number_to_pick_up < validFileNumber:
            raise ValueError('-np {0} is lower than -n ' \
                             '{1}'.format(number_to_pick_up, validFileNumber))


    number_to_pick_up = get_number_to_pick_up(root, number_to_pick_up,
                                              lowest=validFileNumber)
    if verbose and number_to_pick_up:
        print 'pick up {0} files'.format(number_to_pick_up)

    count = 0
    imeis = os.listdir(root)
    createDir(os.path.join(target, 'train'))
    createDir(os.path.join(target, 'test'))

    # put imei_first to be the first one
    if imei_first and not imei_specific:
        imeis.remove(imei_first)
        imeis.insert(0, imei_first)

    for imei_index, imei in enumerate(imeis):
        if imei_specific and imei != imei_specific:
            continue

        user_dir = os.path.join(root, imei)
        if file_specific and imei_specific:
            file_list= [file_specific]
        else:
            file_list = os.listdir(user_dir)

        origin_len = len(file_list)
        if len(file_list) < validFileNumber or len(file_list) < number_to_pick_up:
            # count = count + 1
            if verbose:
                print '-', imei, 'total file number:', str(len(file_list)), 'NOT ENOUGH DISCARD'
            continue
        elif number_to_pick_up:
            # pick up
            file_list = random.sample(file_list, number_to_pick_up)
        else:
            pass

        # count is lable
        if imei_specific:
            if imei_first:
                count = int(imei_first)
            else:
                count = 1
        else:
            count = count + 1

        train_files, test_files = train_test_split(file_list, train_size=proportion)
        dataLoad(user_dir, train_files, 'train', count, target)
        dataLoad(user_dir, test_files, 'test', count, target)

        if verbose:
            print count, imei, 'total file number:', str(origin_len), '->',  str(len(file_list)), 'OK'
