import os
import os.path
import subprocess
import time

from riskserver import data_source
from riskserver import settings
from trainapp.arff2libsvm import arff2svmlight
from trainapp.tools import remove_file, maketestset, testpredict, rename_file, copy_file, append_libsvm, othertests


# TEST_LOG_DIR = os.path.join(settings.BASE_DIR, "testlogfile", "train")

def rmdirfile(folder):
    for file in os.listdir(folder):
        file_dir = os.path.join(folder, file)
        if os.path.isfile(file_dir):
            remove_file(file_dir)


def updatepredict(imei, state, Nselftest, Nothertest, media_path):
    selftest = Nselftest + '.new'
    othertest = Nothertest + '.new'
    if testpredict(imei, state, selftest, othertest) == True:
        print "The update predict answer is True"
        rename_file(os.path.join(settings.BASE_DIR, "model", imei, state, "Npredictor.model"),
                    os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.model"))
        rename_file(selftest, Nselftest)
        rename_file(othertest, Nothertest)
        return True
    else:
        print "The update predict answer is False"
        remove_file(os.path.join(settings.BASE_DIR, "model", imei, state, "Npredictor.model"))
        remove_file(selftest)
        remove_file(othertest)
        os.rmdir(media_path)
        return False


def parse_data(imei, path, state):
    # Converts input file to ARFF format
    print '**** PARSING DATA FOR: {}'.format(imei)
    arff_path = os.path.join(settings.BASE_DIR, "arff", imei)
    print(path)
    cmd = 'org2arff.sh ' + path + ' ' + arff_path
    print '## TRACE ##', 'convert input file to arff', cmd
    print(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    p.wait()
    lines = p.communicate()
    f = open(os.path.join(settings.BASE_DIR, "tmplog.txt"), "w+")
    rmdirfile(path)

    # make 1:5 files to vw
    vw_path = os.path.join(settings.BASE_DIR, "vw_train", imei, state)
    print '******** ' + state + ' VW PATH:', vw_path
    create_path(vw_path)
    solve_state(state, imei, arff_path, vw_path, path)


def solve_state(state, imei, arff_path, vw_path, media_path):
    print(arff_path)

    ISOTIMEFORMAT = '%Y%m%d%H%M%S'
    tag = str(time.strftime(ISOTIMEFORMAT))

    self_filelist = os.path.join(settings.BASE_DIR, imei + tag + state)
    othe_filelist = os.path.join(settings.BASE_DIR, "tx" + tag + state)

    target_arff_file = os.path.join(vw_path, "target" + tag + ".arff")
    target_libsvm_file = os.path.join(vw_path, "target" + tag + ".libsvm")

    target_test_arff_file = os.path.join(vw_path, "target" + ".test.arff")
    target_test_libsvm_file = os.path.join(vw_path, "target" + ".test.libsvm")

    target_othertest_arff_file = os.path.join(vw_path, "target" + "other.test.arff")
    target_othertest_libsvm_file = os.path.join(vw_path, "target" + "other.test.libsvm")

    Nlibsvmpath = os.path.join(vw_path, 'target' + 'Ndata.libsvm')
    libsvmpath = os.path.join(vw_path, 'target' + 'data.libsvm')

    # when use svm, add # on two lines below
    # target_vw_file = os.path.join(vw_path, "target" + tag + ".vw")
    # target_vw_cache_file = os.path.join(vw_path, "target" + tag + ".vw.cache")

    # list files of others and owner self
    list_files(data_source.Other_users_path, state, othe_filelist)
    list_files(arff_path, state, self_filelist)

    # make 1:5
    sectorpath = os.path.join(settings.BASE_DIR, 'trainapp', 'sector.py')
    cmd = 'python ' + sectorpath + ' ' + imei + ' ' + str(data_source.ratio) + ' ' \
          + self_filelist + ' ' + othe_filelist
    print '*** RATIO DATASET BUILDING: {}'.format(cmd)
    print(cmd)
    print '## TRAIN ##', 'building dataset', cmd
    p = subprocess.Popen(cmd, shell=True, stdout=open(target_arff_file, "w"))
    p.wait()
    lines = p.communicate()
    f = open(os.path.join(settings.BASE_DIR, "tmplog.txt"), "w+")

    #
    if os.path.isfile(os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.model")):
        # semi supervise
        # pick up 1/proportion to be tested
        maketestset(target_arff_file, target_test_arff_file, target_othertest_arff_file)

        # convert all to svm and append them behind original svm files
        arff2svmlight(target_test_arff_file, target_test_libsvm_file + '.new')
        append_libsvm(target_test_libsvm_file + '.new', target_test_libsvm_file)
        remove_file(target_test_arff_file)

        arff2svmlight(target_othertest_arff_file, target_othertest_libsvm_file + '.new')
        append_libsvm(target_othertest_libsvm_file + '.new', target_othertest_libsvm_file)
        remove_file(target_othertest_arff_file)

    # generate a new model and check its validate
    arff2svmlight(target_arff_file, target_libsvm_file)
    copy_file(libsvmpath, Nlibsvmpath)
    append_libsvm(Nlibsvmpath, target_libsvm_file)
    # when use svm, add # on two lines below
    # libsvm2vw(target_libsvm_file, target_vw_file)
    # shuff(target_vw_file)

    remove_file(self_filelist)
    remove_file(othe_filelist)
    # shutil.copy(target_arff_file,arff_path + tag + ".arff")
    remove_file(target_arff_file)
    # when use svm, add # on one line below
    # remove_file(target_libsvm_file)

    # when use svm, add # on one line below
    # handle_vw_file(imei, target_vw_file, state)
    # when use nn, add # on one line below
    handle_vw_file(imei, Nlibsvmpath, state)

    if updatepredict(imei, state, target_test_libsvm_file, target_othertest_libsvm_file, media_path):
        rename_file(Nlibsvmpath, libsvmpath)
    else:
        remove_file(Nlibsvmpath)

    # only if one of others performs well in current model, do delete that one in others' set
    othertests(libsvmpath, os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.model"), imei, state)
    remove_file(target_libsvm_file)
    # remove_file(target_othertest_libsvm_file)
    # remove_file(target_test_libsvm_file)
    media_files = os.path.join(settings.BASE_DIR, 'media', imei)
    rmdirfile(os.path.join(arff_path, state))

    # when use svm, add # on two lines below
    # remove_file(target_vw_file)
    # remove_file(target_vw_cache_file)


def list_files(path, key, target):
    print '## TRACE ##', 'listing files at', path, 'to', target
    fp = open(target, "w")
    for rt, dirs, files in os.walk(path):
        for f in files:
            if (key in f) or (key in rt):
                fp.write(os.path.join(rt, f))
                fp.write('\n')
    fp.close()


def create_path(path):
    print '## TRACE ##', 'creating folder', path
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)


def test():
    print(data_source.Other_users_path)
    list_files(data_source.Other_users_path, "walk", "")


def handle_vw_file(imei, vw_path, state):
    target_model_dir = os.path.join(settings.BASE_DIR, "model", imei, state)
    # when use svm, add # on the line below
    # target_model = os.path.join(target_model_dir, "predictor.vw")
    # when use nn, add # on the line below
    target_model = os.path.join(target_model_dir, "Npredictor.model")
    create_path(target_model_dir)
    # Zhengyang beign modify the code
    # change para --passes from 10 to 1
    print "#### make target model " + target_model
    # when use svm, add # on the line below
    # cmd = 'vw -d ' + vw_path + " -c --passes 1 -f " + target_model + " --nn 50 -q nn -b 16"
    # when use nn, add # on the line below
    cmd = 'bin/svm-train -s 0 -t 2 -d 3 -g 0 -r 0 -c 5000 -n 0.5 -p 0.1 -h 1 -b 1 ' + vw_path + ' ' + target_model
    # Zhengyang end modify the code
    print '*** TRAINING: {}'.format(cmd)
    print '## TRACE ##', 'training the model', cmd

    # if state == 'sit':
    #     dest_arff_dir = os.path.join(settings.BASE_DIR, "arff", imei, "sit")
    # else:
    #     dest_arff_dir = os.path.join(settings.BASE_DIR, "arff", imei, "walk")
    # numarff = get_dir_file_number(dest_arff_dir)
    # print '## TRACE ##', 'get file number for', state, ':', numarff

    # test profile
    # when use svm, add # on the line below
    # profile = Profile(os.path.join(TEST_LOG_DIR, "%s_nn_%s_%s" % (imei, numarff, state)))
    # when use nn, add # on the line below
    # profile = Profile(os.path.join(TEST_LOG_DIR, "%s_svm_%s_%s" % (imei, numarff, state)))
    # profile.set()

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    lines = p.communicate()

    # profile.log()

    print '*** TRAINING OUTPUT: {}'.format(lines)

    f = open(os.path.join(settings.BASE_DIR, "tmplog.txt"), "w+")
    print >> f, lines
