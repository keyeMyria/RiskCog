#!/usr/bin/env python

from __future__ import print_function

import random
import sys

sec = 10
basedir = 'F:\python\sector\media\train\arya'
attribute = ["Xmean", "Ymean", "Zmean", "Xvariance", "Yvariance",
             "Zvariance", "XstdDev", "YstdDev", "ZstdDev", "XavgDev", "YaveDev",
             "ZavgDev", "Xskewness", "Yskewness", "Zskewness", "Xkurtosis",
             "Ykurtosis", "Zkurtosis", "Xzcr", "Yzcr", "Zzcr", "Xrms", "Yrms",
             "Zrms", "Xlowest", "Ylowest", "Zlowest", "Xhighest", "Yhighest",
             "Zhighest", "Result", "wXmean", "wYmean", "wZmean", "wXvariance",
             "wYvariance", "wZvariance", "wXstdDev", "wYstdDev", "wZstdDev",
             "wXavgDev", "wYaveDev", "wZavgDev", "wXskewness", "wYskewness",
             "wZskewness", "wXkurtosis", "wYkurtosis", "wZkurtosis", "wXzcr",
             "wYzcr", "wZzcr", "wXrms", "wYrms", "wZrms", "wXlowest", "wYlowest",
             "wZlowest", "wXhighest", "wYhighest", "wZhighest", "wResult", "USER",
             "STATE"]
name_map = {}


def getFloat(s):
    try:
        return float(s)
    except:
        return None


def input_1(file_name, data):
    start = 1
    with open(file_name, 'r') as f:
        for line in f.readlines():
            line = line.split(' ')
            if len(line) == 0:
                continue

            v = []

            if line == "@data":
                start = 1
                continue

            if start == 0:
                continue

            for i in range(len(line) - 2):
                floatVal = getFloat(line[i])
                if line[i] != None:
                    v.append(floatVal)

            v.append(1)
            v.append(0)
            if len(v) != 0:
                data.append(v)


def input_500(fname, data, rest):
    start, cnt = 1, 0
    with open(fname, 'r') as fobj:
        dict = {}
        buff = [x.strip() for x in fobj.readlines()]
        get_num = min(rest, len(buff) / 10)
        while (get_num > 0):
            get_num -= 1
            l = random.choice(buff)
            while (dict.has_key(l)):
                l = random.choice(buff)
            dict[l] = 1
            l = l.split(' ')
            v = []
            cnt += 1
            for i in range(len(l) - 2):
                floatVal = getFloat(l[i])
                if l[i] != None:
                    v.append(floatVal)
            v.append(1)
            v.append(0)
            if len(v) != 0:
                data.append(v)

    return cnt


def print_replace(lst, replace):
    lst[name_map["USER"]] = replace
    for i in range(len(name_map) - 2):
        sys.stdout.write("%0.2f " % lst[i])
    sys.stdout.write("%s %s" % (replace, 0))
    sys.stdout.flush()


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('you should input:python sector.py imei ratio selflist otherlist')

    # get all parameters
    imei = sys.argv[1]
    ratio = int(sys.argv[2])
    self_list = sys.argv[3]
    other_list = sys.argv[4]
    num_of_attribute = len(attribute)

    for i in range(num_of_attribute):
        name_map[attribute[i]] = i

    one_points, five_points = [], []

    # get all other files path
    other_files_path = []
    with open(other_list) as other_list_f:
        for file_path in other_list_f.readlines():
            # remove \n \r \t at the beginning or end
            file_path = file_path.strip()
            if len(file_path) > 0:
                other_files_path.append(file_path)

    with open(self_list) as self_list_f:
        for file_path in self_list_f.readlines():
            # remove \n \r \t at the beginning or end
            file_path = file_path.strip()
            input_1(file_path, one_points)

    # raise ValueError

    self_list_f.close()
    other_list_f.close()
    rest = len(one_points) * ratio
    dict = {}

    while rest > 0:
        rand_file_name = other_files_path[random.randint(0, len(other_files_path) - 1)]
        while (dict.has_key(rand_file_name)):
            rand_file_name = other_files_path[random.randint(0, len(other_files_path) - 1)]
        dict[rand_file_name] = 1
        rest -= input_500(rand_file_name, five_points, rest)

    for item in one_points:
        print_replace(item, 1)
        sys.stdout.write('\n')
        sys.stdout.flush()

    for index in range(len(five_points)):
        print_replace(five_points[index], -1)
        if index != len(five_points) - 1:
            sys.stdout.write('\n')
            sys.stdout.flush()
