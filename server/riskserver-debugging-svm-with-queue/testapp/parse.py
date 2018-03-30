import os
import os.path
import subprocess
import time

from riskserver import data_source
from riskserver import settings
from testapp.shuff import shuff
from trainapp.arff2libsvm import arff2svmlight
from trainapp.libsvm2vw import libsvm2vw
from trainapp.tools import remove_file


def parse_data(imei, path):
    arff_dir = os.path.join(settings.BASE_DIR, "vw_test", imei)
    create_path(arff_dir)
    ISOTIMEFORMAT = '%Y%m%d%H%M%S'
    tag = str(time.strftime(ISOTIMEFORMAT))
    target_arff_file = os.path.join(arff_dir, tag + '.arff')
    target_libsvm_file = os.path.join(arff_dir, tag + '.libsvm')
    # if svm add # below
    # target_vw_file = os.path.join(arff_dir, tag + '.vw')

    # cmd = 'make_arff.exe ' +  path +' 1 1'
    make_arff_path = os.path.join(settings.BASE_DIR, "bin", 'make_arff.exe')
    cmd = make_arff_path + ' ' + path + ' 1 1'
    print(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=open(target_arff_file, "w"))
    p.wait()
    lines = p.communicate()
    f = open(os.path.join(settings.BASE_DIR, "tmplog.txt"), "w+")
    arff2svmlight(target_arff_file, target_libsvm_file)
    # if svm add # before two lines below
    # libsvm2vw(target_libsvm_file, target_vw_file)
    # shuff(target_vw_file)
    remove_file(target_arff_file)
    # if svm add # below
    # remove_file(target_libsvm_file)

    # if svm add # below
    # return target_vw_file
    # if nn add # below
    return target_libsvm_file


def create_path(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)


def test():
    print data_source.Other_users_path
    list_files(data_source.Other_users_path, "walk", "")
