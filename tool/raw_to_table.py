"""
Convert the raw data to a format of table.

Author: Qiang
Date: 3-12-2018
"""
import numpy as np
import os


axises = ['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z', 'grv_x', 'grv_y', 'grv_z']
header = 'acc_x acc_y acc_z gyro_x gyro_y gyro_z grv_x grv_y grv_z'

if __name__ == '__main__':
    path = '/home/cyrus/Public/RiskCog/dataset/test/A0000055849E39/2016-01-26_15_part1'
    filename = path.split('/')[-1]
    target = './'

    raw_data = np.loadtxt(path).reshape(-1, 9)
    np.savetxt(target + filename, raw_data, header=header, fmt='%.10f', comments='')


