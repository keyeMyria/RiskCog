import os
import random
import shutil
import time

from riskserver import settings, data_source
from testapp.score import get_result


def logoutput(fout, str):
    print>> fout, str
    print str


def get_dir_file_number(path):
    print '## TRACE ##', 'counting number of files at', path
    return len(os.listdir(path))


def remove_file(path):
    print '## TRACE ##', 'remove ', path

    if os.path.exists(path):
        os.remove(path)


def make_dir(path):
    print '## TRACE ##', 'mkdir ', path
    if not os.path.exists(path):
        os.mkdir(path)


def rename_file(source, dest):
    print '## TRACE ##', 'rename ', source, ' to ', dest
    if os.path.exists(source):
        if os.path.exists(dest):
            remove_file(dest)
        os.rename(source, dest)


def maketestset(source, dest, otherdes):
    print '## TRACE ##', 'generate self test set files at', dest
    print '## TRACE ##', 'generate others test set files at', otherdes
    f = open(source, 'r')
    buff = [x.strip() for x in f.readlines()]
    buff1 = []
    test = []
    for index in range(len(buff)):
        if (buff[index].split(' ')[-2] == '1'):
            test.append(buff[index])
        else:
            buff1.append(buff[index])
    random.shuffle(test)
    buff = buff1[len(buff1) / data_source.Trainproportion:] + test[len(test) / data_source.Trainproportion:]
    buff1 = buff1[:len(buff1) / data_source.Trainproportion]
    test = test[:len(test) / data_source.Trainproportion]
    f.close()
    outtrain = open(source, 'w')
    for x in buff:
        print>> outtrain, x
    outtrain.close()
    outtest = open(dest, 'w')
    for x in test:
        print>> outtest, x
    outtest.close()

    output = open(otherdes, 'w')
    for x in buff1:
        print>> output, x
    output.close()


def makefilelist(source, listname):
    print '## TRACE ##', 'listing files at', source, 'to', listname
    f = open(listname, 'w')
    for x in os.listdir(source):
        print>> f, x.split('.')[0]


def copy_file(sour, dest):
    if os.path.exists(dest):
        remove_file(dest)
    if not os.path.exists(sour):
        os.mknod(dest)
    else:
        shutil.copy(sour, dest)


def append_libsvm(sour, ins):
    if not os.path.exists(sour):
        os.mknod(sour)
    if not os.path.exists(ins):
        os.mknod(ins)
    fout = open(sour, 'a')
    fin = open(ins, 'r')
    buff = [x.strip() for x in fin.readlines()]
    for x in buff:
        if x != '':
            print>> fout, x
    fin.close()
    fout.close()


def get_dir_file_num_contain(path, string):
    print '## TRACE ##', 'find count at ', path, 'with string', string
    cnt = 0
    if os.path.exists(path):
        for dirpath, dirs, files in os.walk(path):
            for filenames in files:
                if string in filenames:
                    cnt += 1
        return cnt
    else:
        return 0


def testanswer(filename, vw_path, imei, state):
    if not os.path.exists(vw_path):
        print 'svm model is not exists'
        return 0
    if not os.path.exists(filename):
        print 'filename is not a file or not exists'
        return 0
    result_dir = os.path.join(settings.BASE_DIR, "result", imei)
    make_dir(result_dir)
    ISOTIMEFORMAT = '%Y%m%d%H%M%S'
    time_stamp = str(time.strftime(ISOTIMEFORMAT))
    result_path = os.path.join(result_dir, "results.txt_%s_%s" % (state, time_stamp))
    cmd = "bin/svm-predict -b 1 " + filename + " " + vw_path + " " + result_path
    print '## TRACE ##', 'training', cmd
    output = os.popen(cmd)
    print(output.read())
    res_acc, res_pre, res_rec = get_result(result_path)
    remove_file(result_path)
    return res_acc


def othertests(filename, vw_path, imei, state):
    result_dir = os.path.join(settings.BASE_DIR, "result", imei)
    make_dir(result_dir)
    ISOTIMEFORMAT = '%Y%m%d%H%M%S'
    time_stamp = str(time.strftime(ISOTIMEFORMAT))
    result_path = os.path.join(result_dir, "results.txt_%s_%s" % (state, time_stamp))
    cmd = "bin/svm-predict -b 1 " + filename + " " + vw_path + " " + result_path
    print '## TRACE ##', 'training', cmd
    output = os.popen(cmd)
    print(output.read())
    f = open(result_path, 'r')
    buffer = [x.strip() for x in f.readlines()]
    f.close()
    f = open(filename, 'r')
    other = [x.strip() for x in f.readlines()]
    f.close()
    out = []
    for x in range(len(other)):
        y = buffer[x + 1].split()
        if not (y[0] == '1' and y[3] == '-1'):
            out.append(other[x])
    f = open(filename, 'w')
    for x in out:
        print>> f, x
    f.close()
    remove_file(result_path)


def testpredict(imei, state, selftest, othertest):
    fout = open(os.path.join(settings.BASE_DIR, "model", imei, state, 'ACC.log'), 'a')
    if not os.path.isfile(os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.model")):
        print "## TRACE ## The first time"
        return True

    Npredict_self = testanswer(selftest, os.path.join(settings.BASE_DIR, "model", imei, state, "Npredictor.model"),
                               imei, state)
    Npredict_other = 1 - testanswer(othertest,
                                    os.path.join(settings.BASE_DIR, "model", imei, state, "Npredictor.model"), imei,
                                    state)
    predict_self = testanswer(selftest, os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.model"), imei,
                              state)
    predict_other = 1 - testanswer(othertest, os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.model"),
                                   imei, state)
    logoutput(fout, imei + ' ACC of this times:')
    logoutput(fout, "Npredict_self:%.2f%%" % (Npredict_self * 100))
    logoutput(fout, "Npredict_other:%.2f%%" % (Npredict_other * 100))
    logoutput(fout, "predict_self:%.2f%%" % (predict_self * 100))
    logoutput(fout, "predict_other:%.2f%%" % (predict_other * 100))
    fout.close()

    if (Npredict_other + Npredict_self - predict_other - predict_self < data_source.testpredict_refuse_ACC):
        return False
    else:
        return True
