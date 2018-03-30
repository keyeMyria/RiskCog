#!/usr/bin/python 
import os
import os.path
import requests,random,time
import json

# test_url = 'http://127.0.0.1:8000/test/'
# iquery_url = 'http://127.0.0.1:8000/query/'
test_url = 'http://10.214.148.124:8000/test/'
query_url = 'http://10.214.148.124:8000/query/'

# test_url = 'http://139.224.207.24:8000/test/'
# query_url = 'http://139.224.207.24:8000/query/'

#test_url = 'http://garuda.cs.northwestern.edu:8080/test/'
#query_url = 'http://garuda.cs.northwestern.edu:8080/query/'

imei = 'prediction_test'
test_file_path = "other"

test_files = os.listdir(test_file_path)

for file_name in test_files:
    print "### now test file : " + file_name
    file_path = os.path.join(test_file_path, file_name)
    post_data = {
            'imei' : imei
    }
    post_file = {
        'path' : open(file_path,'rb')
    }

    response = requests.post(test_url, data=post_data, files = post_file)
    res = response.json()
    max_version = res['max_version']
    post_data = {
            'imei' : imei,
            'version' : max_version
    }
    time.sleep(2)
    response = requests.post(query_url, data=post_data, files = post_file)
    fp = open("report_prediction_test_other.txt","a")
    print>>fp,   file_name + "\t" ,
    print>>fp,   response.json()
    fp.close()

