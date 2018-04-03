"""
cat separated sensor data files into one file
==================

Say we have 3 sensor data files called acc_x, acc_y, acc_z, we will generate a file as below
    acc_x[0]
    acc_y[0]
    acc_z[0]
    acc_x[1]
    acc_y[1]
    acc_z[1]
    ...
make sure there is more than 100 lines in one sensor data file
IN FACT, without the source code of 'make_arff.exe', we have to 'add' one sensor using one existed two times.

:author:
- cyrus

:date: 2018-04-01
"""
import numpy as np
import os
import random


def sensor_cat(root, target, separated_sensor_filenames):
    """
    see top of this file

    :param root: path to source data set
    :param target: target to target data set
    :param separated_sensor_filenames: names to sensor file
    :return: XXX/raw_data with same file structure as root
    """
    X = []
    for ssf in separated_sensor_filenames:
        with open(os.path.join(root, ssf)) as f:
            X.append([line.strip() for line in f])
    X = np.array(X).T
    print X.shape
    # X = np.append(X, X[:, 0:3], axis=1)
    # TODO recognize it rather than write a '-4'
    target = os.path.join(target, '/'.join(root.split('/')[-4:]))
    os.system('mkdir -p {0}'.format(target))
    np.savetxt(os.path.join(target, 'raw_data'), X, fmt='%s', delimiter='\n')


def test_main(root, target, separated_sensor_filenames):
    N = random.randint(1, 100)

    samples = []
    for ssf in separated_sensor_filenames:
        with open(os.path.join(root, ssf)) as f:
            samples.append(f.readlines()[N])

    lssf = len(separated_sensor_filenames)
    # lssf = len(separated_sensor_filenames) + 3
    # TODO recognize it rather than write a '-4'
    target = os.path.join(target, '/'.join(root.split('/')[-4:]))
    with open(os.path.join(target, 'raw_data')) as f:
        samples_to_check = f.readlines()[lssf * N: lssf * (N + 1)]
        # samples_to_check = f.readlines()[lssf * N: lssf * (N + 1)][0:6]
    assert samples == samples_to_check
    return True


if __name__ == '__main__':
    separated_sensor_filenames = [
        'acc_x.txt',
        'acc_y.txt',
        'acc_z.txt',
        'gyro_x.txt',
        'gyro_y.txt',
        'gyro_z.txt',
    ]

    root = '/home/cyrus/Public/RiskCog/dataset/mimicry'
    target = '/home/cyrus/Public/RiskCog/dataset/mimicry_raw'
    os.system('rm -rf {0}'.format(target))
    for root_, dir_, _ in os.walk(root):
        if len(dir_) == 0:
            sensor_cat(root_, target, separated_sensor_filenames)
            # do test
            if not test_main(root_, target, separated_sensor_filenames):
                raise ValueError('something wrong')

    print '>> done'
