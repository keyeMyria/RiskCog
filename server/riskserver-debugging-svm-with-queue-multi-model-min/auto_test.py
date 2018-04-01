# coding=utf-8
#  !/usr/bin/python

"""
测试说明
准备测试集并以imei命名
imei文件夹内应直接为测试数据

配置test和query的url和测试集所在dir
配置target_imei

如存在test.log, 删除它可重新开始
"""

import os

import requests

test_file_root = '/home/cyrus/Public/data_of_riskcog/data_of_huawei_by_28_11_2017/test_t'
test_imeis = os.listdir(test_file_root)

target_imeis = [
    '357143042200839',
    '861955030016110',
    '863445032682661',
    '864360034755739',
    '865166027552671',
    '866158030126253',
    '866789028522770',
]

test_url = 'http://127.0.0.1:8000/test/'
query_url = 'http://127.0.0.1:8000/query/'

with open('test.log', 'a+') as f:
    files = f.readlines()
    f.close()

for target_imei in target_imeis:
    for test_imei in test_imeis:
        test_file_dir = os.path.join(test_file_root, test_imei)
        if not os.path.isdir(test_file_dir):
            continue

        # begin
        test_files = os.listdir(os.path.join(test_file_root, test_imei))

        for file_name in test_files:
            if '{2}/{0}/{1}\n'.format(test_imei, file_name, target_imei) not in files:
                # test
                file_path = os.path.join(test_file_dir, file_name)
                post_data = dict(test_imei=test_imei, target_imei=target_imei)
                post_file = dict(path=open(file_path, 'rb'))

                print('test_imei:{0} target_imei:{1} {2}'.format(test_imei,
                                                                 target_imei,
                                                                 file_name))
                response = requests.post(test_url, data=post_data, files=post_file)
                res = response.json()
                max_version = res['max_version']
                print(res)

                # query
                post_data = {'test_imei': test_imei, 'target_imei': target_imei, 'version': max_version}
                response = requests.post(query_url, data=post_data)
                print(response.json())
                with open('test.log', 'a') as f:
                    f.write('{2}/{0}/{1}\n'.format(test_imei, file_name,
                                                   target_imei))
                    f.close()
            else:
                print ('tested before {0}:{1} to {2}'.format(test_imei,
                                                             file_name,
                                                             target_imei))
os.remove('test.log')
import pynotify

pynotify.init('finish bubble')
bubble_notify = pynotify.Notification('Notification', 'Test for {0} complete'.format(target_imei))
bubble_notify.show()
