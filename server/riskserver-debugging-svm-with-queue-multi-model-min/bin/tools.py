import os
import random
import shutil
import subprocess
import tempfile
import time
from django.core.exceptions import ObjectDoesNotExist

import django_rq
import numpy as np

from bin.arff2libsvm import arff2svmlight, dim_redu
from riskserver import data_source, settings
from trainapp.models import User


def median(lst):
    if not lst:
        return
    if len(lst) % 2 == 1:
        return lst[len(lst) // 2]
    else:
        sum = lst[len(lst) // 2 - 1]
        sum = sum + lst[len(lst) // 2]
        sum = sum / 2.0
        return sum


def check_is_flat(path):
    """
    return if a file is flat or not

    :param path: absolute path
    :return: True/False
    """

    with open(path) as f:
        lines = f.readlines()
        f.close()

    gx = []
    gy = []
    gz = []
    for i in range(0, len(lines), 9):
        gx.append(lines[i + 6])
        gy.append(lines[i + 7])
        gz.append(lines[i + 8])

    gx = [float(x) for x in gx]
    gy = [float(x) for x in gy]
    gz = [float(x) for x in gz]

    if (abs(median(gx)) <= 1.5 and abs(median(gy)) <= 1.5 and
                abs(median(gz)) < 10 and abs(median(gz) >= 9)):
        return True
    return False


def get_sensor_vector(path, method='mean'):
    """
    get a mean or median vector for every file

    There are a time sequence in every raw file,
    at here, we calculate the mean or median of this sequence.

    A vector denotes [ax, ay, az, gyx, gyy, gyz, gx, gy, gz]


    :param path: path or path list
    :param method: mean or median
    :return: list like [vector1, vector2]
    """

    vectors = []
    for p in path:
        with open(p) as f:
            lines = f.readlines()
            f.close()

        vector = [[] for i in range(0, 9)]

        for i in range(0, len(lines), 9):
            for k in range(0, 9):
                vector[k].append(float(lines[i + k]))
        if method == 'mean':
            vector = [np.ceil(np.mean(vector[j]) * 1000) for j in range(0, 9)]
        elif method == 'median':
            vector = [np.ceil(np.median(vector[j]) * 1000) for j in range(0, 9)]
        else:
            raise NotImplementedError('')
        vectors.append(vector)

    return vectors


def count_lines(path):
    with open(path) as f:
        lines = f.readlines()
    return len(lines)


def make_test_set(pick_up_arff, train_set, test_set_from_yourself, test_set_from_others, properation):
    with open(pick_up_arff) as f:
        # data = [x.strip() for x in f.readlines()]
        data = [x for x in f.readlines()]
        f.close()

    # get data of yourself and others respectively
    data_for_others = []
    data_for_yourself = []
    for index in range(len(data)):
        if data[index].split(' ')[-2] == '1':
            data_for_yourself.append(data[index])
        else:
            data_for_others.append(data[index])
    random.shuffle(data_for_yourself)

    # train_set: 1/train_proportion -> end
    train = data_for_others[len(data_for_others) / properation:] \
            + data_for_yourself[len(data_for_yourself) / properation:]
    # test_set: begin -> 1/train_proportion
    test_for_yourself = data_for_yourself[:len(data_for_yourself) / properation]
    test_for_others = data_for_others[:len(data_for_others) / properation]

    with open(train_set, 'w') as f_train_set:
        f_train_set.writelines(train)
        f_train_set.close()
    with open(test_set_from_yourself, 'w') as f_test_set_from_yourself:
        f_test_set_from_yourself.writelines(test_for_yourself)
        f_test_set_from_yourself.close()
    with open(test_set_from_others, 'w') as f_test_set_from_others:
        f_test_set_from_others.writelines(test_for_others)
        f_test_set_from_others.close()


def list_files(path, state, target):
    # print '## TRACE ##', 'listing files at', path, 'to', target
    fp = open(target, "w")
    for root, dirs, files in os.walk(path):
        for f in files:
            if (state in f) or (state in root):
                fp.write(os.path.join(root, f))
                fp.write('\n')
    fp.close()


def get_dir_file_number(path):
    print '## TRACE ##', 'counting number of files at', path
    return len(os.listdir(path))


def remove_file(path):
    print '## TRACE ##', 'remove ', path

    if os.path.exists(path):
        os.remove(path)


def make_dir(path):
    # print '## TRACE ##', 'mkdir ', path
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
    buff = buff1[len(buff1) / data_source.TRAIN_PROPORTION:] + test[len(test) / data_source.TRAIN_PROPORTION:]
    buff1 = buff1[:len(buff1) / data_source.TRAIN_PROPORTION]
    test = test[:len(test) / data_source.TRAIN_PROPORTION]
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


def org_to_libsvm(source_path, state):
    # text -> arff
    temp_arff = tempfile.NamedTemporaryFile(dir=settings.TEMP_ROOT, delete=False)
    cmd = settings.BASE_DIR + '/bin/make_arff.exe' + ' ' + source_path + ' 1 ' + state
    p = subprocess.call(cmd, shell=True, stdout=temp_arff)  # block
    # temp_arff.seek(0) # alter file pointer if you want read it directly
    # arff -> libsvm
    temp_libsvm = tempfile.NamedTemporaryFile(dir=settings.TEMP_ROOT, delete=False)
    arff2svmlight(temp_arff.name, temp_libsvm.name)
    temp_arff.close()
    os.remove(temp_arff.name)  # manual delete
    return temp_libsvm


def org_to_arff(source_path, state):
    # text -> arff
    temp_arff = tempfile.TemporaryFile(dir=settings.TEMP_ROOT)
    cmd = settings.BASE_DIR + '/bin/make_arff.exe' + ' ' + source_path + ' 1 ' + state
    p = subprocess.call(cmd, shell=True, stdout=temp_arff)  # block

    return temp_arff


def arff_to_svmlight(source):
    """
    similar to arff2svmlight, but source should be a file handler

    `arff2svmlight` converts a data file in arff format
    to the libsvm's svmlight format.
    Format details are here: http://leon.bottou.org/projects/lasvm (Implementation section)

    The gist:
    <line>    = <target> <feature>:<value> ... <feature>:<value>
    <target>  = +1 | -1  <int>
    <feature> = <integer>
    <value>   = <float>
    """

    # print '## TRACE ##', 'converting arff to svmlight', source, destination
    # TODO: fix the way of specifying the label
    # TARGET_FLAG = 1  can be either +1 or -1

    temp_svmlight = tempfile.TemporaryFile(dir=settings.TEMP_ROOT)

    source.seek(0)
    for line in source.readlines():
        # process each line from the arff file
        if "nan" in line.lower() or line.strip() == '':
            # skip the nan line
            continue
        line = line.strip()
        features = line.split()
        # TODO: check this -- some features to ignore
        postural_data = features[-1]  # TODO: should this be included?
        imei_number = features[-2]  # TODO: should this be ignored?

        # convert each feature to the appropriate format in svmlight format.
        format = '%s %s\n'
        arff = imei_number + ' ' + ' '.join([
            ':'.join(i) for i in zip([
                str(num) for num in range(len(features))
            ], features[:-2])  # TODO: ignoring last 2 features. get this clarified.
        ])
        buf = dim_redu(arff, [0, 7, 8, 9], features[-2])
        temp_svmlight.write('%s\n' % (buf))
    return temp_svmlight


def get_name():
    iso_time_format = '%Y%m%d%H%M%S'
    return str(time.strftime(iso_time_format))


def get_or_create_user(imei, create=True):
    """
    save/get the user's information

    :param create: if not find this user in database, create it or not
    :param imei: imei
    :return: User Object or None
    """

    try:
        user = User.objects.get(imei=imei)
    except ObjectDoesNotExist:
        user = User.objects.create(imei=imei)
        if create:
            # initial user resources
            # dirs or files under /media/ will be created automatically
            # but those under /model/ have to be created manually
            make_dir(os.path.join(settings.MODEL_BOX_ROOT, imei))
            make_dir(os.path.join(settings.MODEL_BOX_ROOT, imei, 'sit'))
            make_dir(os.path.join(settings.MODEL_BOX_ROOT, imei, 'walk'))
    return user


def file_check(path):
    """
    return lie or not, sit or walk

    :param path: absolute path
    :return: lie or not, 'sit' or 'walk'
    """

    # check lie
    is_flat = check_is_flat(path)
    # check sit or walk
    cmd = settings.BASE_DIR + '/bin/check_sit_or_walk.exe' + ' ' + path
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    # p.stout.readline is like '/tmp/tmpXum96Z.upload\t0.600926\n'
    # p.stdout.readline().split() will be ['/tmp/tmpXum96Z.upload', '0.600926']
    return_sit_or_walk = float(p.stdout.readline().split()[1])

    if return_sit_or_walk > data_source.SIT_OR_WALK_THRESHOLD:
        state = 'walk'
    else:
        state = 'sit'

    return is_flat, state


def clear_queue(user, size, model_box_order, state):
    """
    clear redundancy task

    :param user:
    :param size:
    :param model_box_order:
    :param state:
    :return:
    """
    queue = django_rq.get_queue('trainer')
    jobs = queue.get_jobs()
    ids_removed = []

    for job in jobs:
        current_imei = job.args[0].imei
        current_file_number = len(job.args[1])
        current_model_box = job.args[2]
        current_state = job.args[3]
        current_queue_id = job.id

        if current_imei == user.imei and current_model_box == model_box_order and current_state == state:
            if current_file_number <= size:
                ids_removed.append(current_queue_id)
                queue.remove(current_queue_id)
    return ids_removed
