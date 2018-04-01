# coding=utf-8
# !/usr/bin/python

"""
测试说明
准备训练集并以imei命名
imei文件夹内应直接为测试数据

配置train的url和测试集所在dir

如存在train.log, 删除它可重新开始
"""

import os.path
import time

import requests

train_file_root = '/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/train_t'
imeis = os.listdir(train_file_root)
url = 'http://127.0.0.1:8000/train/'

with open('train.log', 'a+') as f:
    files = f.readlines()
    f.close()

for imei in imeis:
    train_file_dir = os.path.join(train_file_root, imei)
    if not os.path.isdir(train_file_dir):
        continue

    # prepare
    train_files = os.listdir(train_file_dir)

    for file_name in train_files:
        if '{0}/{1}\n'.format(imei, file_name) not in files:
            post_data = {'imei': imei}
            file_path = os.path.join(train_file_dir, file_name)
            post_file = {'path': open(file_path, 'rb')}

            print ('train {0}/{1}'.format(imei, file_name))
            response = requests.post(url, data=post_data, files=post_file)
            print(response.json())
            with open('train.log', 'a') as f:
                f.write('{0}/{1}\n'.format(imei, file_name))
                f.close()
            time.sleep(1)
        else:
            print ('trained before')
os.remove('train.log')
