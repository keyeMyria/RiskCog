#!/usr/bin/python 
import os
import os.path
import requests,random,time

url = 'http://127.0.0.1:8000/train/'
#url = 'http://10.214.148.124:8000/train/'
#url = 'http://garuda.cs.northwestern.edu:8080/train/'
# train_file_path = "train"
# train_file_path = "861955030016110_100_5_0.2"
# train_file_path = "861955030016110_100_5_0.05"
# train_file_path = "861955030016110_100_10_0.05"
train_file_path = "863445032682661_1"
# train_file_path = "866789028522770"
imei = 'train'
# imei = '861955030016110_100_5_0.2'
# imei = '861955030016110_100_5_0.05'
# imei = '861955030016110_100_10_0.05'
imei = '863445032682661_1'
# imei = '866789028522770'

#random select number2start files to train
train_files = os.listdir(train_file_path)

#post these files
i = 0
for file_name in train_files:
    post_data = {
        'imei' : imei
    }
    file_path = os.path.join(train_file_path, file_name)
    post_file = {
        'path' : open(file_path,'rb')
    }
    response = requests.post(url, data=post_data, files = post_file)
    print(file_path)
    print(response.json())
    time.sleep(0.75)
    i += 1
