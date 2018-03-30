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


def input_1(fname, data):
    start = 1
    with open(fname, 'r') as fobj:
        for l in fobj.readlines():
            l = l.split(' ')
            if len(l) == 0:
                continue

            v = []

            if l == "@data":
                start = 1
                continue

            if start == 0:
                continue

            for i in range(len(l) - 2):
                floatVal = getFloat(l[i])
                if l[i] != None:
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
        print 'you sholid input:python sector.py imei ratio selflist otherlist'
    imei = sys.argv[1]
    oratio = int(sys.argv[2])
    selflist = sys.argv[3]
    otherlist = sys.argv[4]
    num_of_attribute = len(attribute)
    for i in range(num_of_attribute):
        name_map[attribute[i]] = i

    one_points, five_points = [], []
    files = []
    selfin = open(selflist, 'r')
    otherin = open(otherlist, 'r')
    for l in otherin.readlines():
        l = l.strip()
        if len(l) > 0:
            files.append(l)
    for ff in selfin.readlines():
        ff = ff.strip()
        input_1(ff, one_points)
    selfin.close()
    otherin.close()
    rest = len(one_points) * oratio
    dict = {}
    while rest > 0:
        rand_file_name = files[random.randint(0, len(files) - 1)]
        while (dict.has_key(rand_file_name)):
            rand_file_name = files[random.randint(0, len(files) - 1)]
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
