import json
import time

import requests

imei = raw_input("Enter IMEI >>").strip()

base_path = '/home/sandeep/portal/chosen/'

# original_imei = '352787060708993'

# train_files = [20160907032421, 20160907032759, 20160907032846, 20160907033003, 20160907033021, 20160907033140, 20160907033446, 20160907033527, 20160907033617, 20160907033646, 20160907033710, 20160907034048, 20160907034102, 20160907042523, 20160907042612, 20160907042622, 20160907042713, 20160907042749, 20160907054922, 20160907054923, 20160907054924, 20160907055002, 20160907055028, 20160907055201, 20160907060804, 20160907060809, 20160907061417, 20160907061424, 20160907061452, 20160907061513, 20160907061557, 20160907061831, 20160907061943, 20160907062322, 20160907062359, 20160907062436, 20160907063611, 20160907064201, 20160907064216, 20160907064234, 20160907065714, 20160907065814, 20160907065910, 20160907065924, 20160907065940, 20160907070107, 20160907070242, 20160907070357, 20160907070905, 20160907071130, 20160907071312, 20160907071516, 20160907071756, 20160907071839, 20160907072012, 20160907072138, 20160907072226, 20160907072712, 20160907073308, 20160907073329, 20160907073350, 20160907073503, 20160907074311, 20160907074402, 20160907074505, 20160907074513, 20160907074522, 20160907074535, 20160907074602, 20160907075000, 20160907075014, 20160907075117, 20160907075141, 20160907075208, 20160907075341, 20160907095035, 20160907095305, 20160907095359, 20160907095409, 20160907095423, 20160907095608, 20160907095626, 20160907095854, 20160907095902, 20160907095903, 20160907095929, 20160907095941, 20160907100011, 20160907100029, 20160907100042, 20160907100059, 20160907100120, 20160921133955, 20160921134004, 20160921134029, 20160921134054, 20160921134135, 20160921134140, 20160921134346, 20160921135037, 20160921135129, 20160921135152, 20160921135156, 20160921135205, 20160921135218, 20160925023035, 20160925023059, 20160925023106, 20160925023118, 20160925023519, 20160925023532, 20160925024042, 20160925024050, 20160925024222, 20160925024234, 20160925025305, 20160925025408, 20160925025558, 20160925025616, 20160925025731, 20160925030037, 20160925030105, 20160925030128, 20160925030538, 20160925030616, 20160925030737, 20160925030750, 20160925030849, 20160925030911, 20160925030915, 20160925031414, 20160925031657, 20160925032200, 20160925032253]


original_imei = 'sandeep'

train_files = [20161127063409, 20161127064437, 20161127064501, 20161127065739, 20161127065841, 20161127065856,
               20161127065957, 20161127070001, 20161127070108, 20161127070309, 20161127070408, 20161127070411,
               20161127070537, 20161127070542, 20161127070646, 20161127070646, 20161127070807, 20161127070835,
               20161127071006, 20161127071107, 20161127071107, 20161127071237, 20161127071238, 20161127071408,
               20161127071408, 20161127071537, 20161127071538, 20161127071708, 20161127071708, 20161127071838,
               20161127071839, 20161127072008, 20161127072009, 20161127072142, 20161127072142, 20161127072317,
               20161127072317, 20161127072451, 20161127072451, 20161127072625, 20161127072625, 20161127072804,
               20161127072804, 20161127072942, 20161127072942, 20161127073115, 20161127073115, 20161127094456,
               20161127094456, 20161127094612, 20161127094822, 20161127094822, 20161127095250, 20161127095350,
               20161127095350, 20161127095520, 20161127095520, 20161127095821, 20161127095821, 20161127095951,
               20161127095951, 20161127100027, 20161127101505, 20161127101605, 20161127101605, 20161127101735,
               20161127101735, 20161127101906, 20161127101906, 20161127101954, 20161127101954, 20161127102001,
               20161127102210, 20161127102210, 20161127171103, 20161127173109, 20161127173210, 20161127173210,
               20161127173302, 20161127173331, 20161127173401, 20161127173431, 20161127173454, 20161127181240,
               20161127194202, 20161127194211, 20161127200438, 20161127200727, 20161127200828, 20161127200828,
               20161127210713, 20161127210813, 20161127210843, 20161128031514]

test_files = []

# sort based on earliest time
train_files.sort(key=lambda x: int(x))
test_files.sort(key=lambda x: int(x))


def sandeep():
    print requests.get('http://localhost:8000/sandeep/').text


def train(imei, file_path):  # returns imei, result code, numfiles
    files = {'path': open(file_path, 'rb')}
    data = {'imei': imei}
    r = requests.post('http://localhost:8000/train/', files=files, data=data)
    print r.text


def test(imei, file_path):  # returns max version which can be passed to query
    files = {'path': open(file_path, 'rb')}
    data = {'imei': imei}
    r = requests.post('http://localhost:8000/test/', files=files, data=data)
    print r.text
    return json.loads(r.text)['max_version']


def ask_trained(imei, version):  # returns 'trained' or not
    data = {'imei': imei, 'version': version}
    r = requests.post('http://localhost:8000/ask_trained/', data=data)
    print r.text
    return r.text


def query(imei, version):  # used to get the summary ('result', 'version')
    data = {'imei': imei, 'version': version}
    r = requests.post('http://localhost:8000/query/', data=data)
    print r.text
    return r.text


def manual_fix(imei, version, signal):  # fixes a version. signal is either 0 or 1
    data = {'imei': imei, 'version': version, 'signal': signal}
    r = requests.post('http://localhost:8000/manual_fix/', data=data)
    print r.text
    # returns 'imei' and 'received_signal'


# MAIN PROCESSNG LOOP

# testing server
sandeep()

f = open('./result.log', 'w')
datapoints = train_files
# [:10] + test_files

i = 0
latest_version = 0
while True:
    print 'loading data point number: {}'.format(i)
    print 'working on imei: {}'.format(imei)
    print 'pick your choice:'
    print '* train'
    print '* test'
    print '* ask'
    print '* query'
    print '* manual'
    print '* exit'

    choice = raw_input("choice >>").strip()

    # if i < 10:
    #     choice = 'train'
    # else:
    #     choice = 'test'

    if choice == 'train':
        # train code here
        try:
            file_path = base_path + 'train/' + original_imei + '/' + str(datapoints[i])
            train(imei, file_path)
            time.sleep(1.0)
            res = ask_trained(imei, latest_version)
            f.write(json.loads(res.replace('\n', '|'))['result'] + "\n")
        except Exception as e:
            print e
            if str(e) == "list index out of range":
                break
        i += 1
    elif choice == 'test':
        # test code here
        try:
            file_path = base_path + 'train/' + original_imei + '/' + str(datapoints[i])
            latest_version = test(imei, file_path)
            print 'latest_version', latest_version
            time.sleep(3)
            res = query(imei, latest_version)
            f.write(json.loads(res.replace('\n', '|'))['result'] + "\n")
        except Exception as e:
            print e
            if str(e) == "list index out of range":
                break
        i += 1
    elif choice == 'ask':
        # ask trained code here
        ask_trained(imei, latest_version)
    elif choice == 'query':
        # query code here
        query(imei, latest_version)
        pass
    elif choice == 'manual':
        # manual code here
        signal = raw_input("signal >>").strip()
        manual_fix(imei, latest_version, signal)
    elif choice == 'exit':
        break
    else:
        print 'oops, typo?'
