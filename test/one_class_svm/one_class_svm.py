"""
one class svm test
==================

:author:
    - cyrus

:date: 2018-04-01
"""
import os
import random
import numpy as np

MAX_NUM_IMAGES_PER_CLASS = 2 ** 27 - 1  # 134M
MIN_NUM_IMAGES_PER_CLASS = 0  # default 10
TRAIN = 'Train'  # default: train
TEST = 'Test'  # default: test
# MIN_NUM_IMAGES_PER_CLASS = 10  # default 10
# TRAIN = 'train' # default: train
# TEST = 'test' # default: test
BIN_ROOT = None


def preprocessing(dataset_dir):
    """
    file structure of dataset is as below:
    ::

        dataset
           |-- train
           |    |-- user1
           |    |     |-- file1
           |    |     |-- file2
           |    |-- user2
           |          |-- file1
           |          |-- file1
           |-- test
                |-- user1
                |     |-- file1
                |     |-- file1
                |-- user2
                     |-- file1
                     |-- file1

    if there is no `test` under `dataset`, we will split `train` into 3 pieces `train` `validation` and `test` by 8:1:1,
    or into 2 pieces `train` and `validation` by 8:2

    :param dataset_dir: dir to dataset
    :return: return training, validation, testing set and others
    """
    # check structure
    if not os.path.exists(dataset_dir):
        raise ValueError('dir to dataset {0} not exists'.format(dataset_dir))
    types = os.listdir(dataset_dir)
    if TRAIN not in types:
        raise ValueError('dir to train not exists')

    # declare what we return
    training_filepaths, validation_filepaths, testing_filepaths = [], [], []

    # split dataset into 2 or 3 parts
    users = os.listdir(os.path.join(dataset_dir, TRAIN))
    for user in users:
        filenames = os.listdir(os.path.join(dataset_dir, TRAIN, user))
        for filename in filenames:
            filepath = os.path.join(dataset_dir, TRAIN, user, filename)
            if filepath.endswith('arff') or filepath.endswith('libsvm'):
                os.system('rm {0}'.format(filepath))

        # make the shuffle result unchangeable
        random.seed(0)
        filenames = os.listdir(os.path.join(dataset_dir, TRAIN, user))
        random.shuffle(filenames)

        if len(filenames) < MIN_NUM_IMAGES_PER_CLASS:
            raise ValueError('files for {0} is less than 10, which is not enough'.format(user))

        for index, filename in enumerate(filenames):
            filepath = os.path.join(dataset_dir, TRAIN, user, filename)
            if TEST not in types:
                if index / float(len(filenames)) >= .90:
                    testing_filepaths.append(filepath)
                elif index / float(len(filenames)) >= .80:
                    validation_filepaths.append(filepath)
                else:
                    training_filepaths.append(filepath)
            else:
                if index / float(len(filenames)) >= .80:
                    validation_filepaths.append(filepath)
                else:
                    training_filepaths.append(filepath)

    # add filepaths into testing set
    if TEST in types:
        testing_users = os.listdir(os.path.join(dataset_dir, TEST))
        for testing_user in testing_users:
            filenames = os.listdir(os.path.join(dataset_dir, TEST, testing_user))
            for filename in filenames:
                filepath = os.path.join(dataset_dir, TEST, testing_user, filename)
                if filepath.endswith('arff') or filepath.endswith('libsvm'):
                    os.system('rm {0}'.format(filepath))
                    continue
                testing_filepaths.append(filepath)

    # add filepaths into other set
    if 'other' in types:
        other_filepaths = []
        other_users = os.listdir(os.path.join(dataset_dir, 'other'))
        for other_user in other_users:
            filenames = os.listdir(os.path.join(dataset_dir, 'other', other_user))
            for filename in filenames:
                filepath = os.path.join(dataset_dir, 'other', other_user, filename)
                if filepath.endswith('arff') or filepath.endswith('libsvm'):
                    os.system('rm {0}'.format(filepath))
                    continue
                other_filepaths.append(filepath)
    else:
        other_filepaths = None

    return training_filepaths, validation_filepaths, testing_filepaths, other_filepaths


def train(dataset_dir, training_filepaths, validation_filepaths, n_classes=2, adversarial=False):
    """
    train using n-class SVM

    :param training_filepaths: filepaths to files in training set
    :param validation_filepaths: filepaths to files in validation set
    :param n_classes: n-classes svm
    :param adversarial: if True, copy the features and paste them with adverse label
    :return: model paths to all users, one of which has a format like `dataset/model/user/user.model`
    """
    # format to arff and then to libsvm
    for filepath in training_filepaths + validation_filepaths:
        os.system('{1}/make_arff.exe '
                  '{0} 1 1 > {0}.arff'.format(filepath, BIN_ROOT))
        os.system("sed -i \"s/\-nan/0/g\" {0}.arff".format(filepath))
        os.system('python {1}/arff2libsvm.py {0} {0}.libsvm'.format('.'.join([filepath, 'arff']), BIN_ROOT))

    # train
    # cat training libsvm files and validation libsvm files
    libsvm_paths = []
    for filepath in training_filepaths + validation_filepaths:
        user = filepath.split('/')[-2]
        libsvm_path = os.path.join(dataset_dir, TRAIN, user, '.'.join([user, 'arff', 'libsvm']))
        os.system('cat {0}.arff.libsvm >> {1}'.format(filepath, libsvm_path))
        if libsvm_path not in libsvm_paths:
            libsvm_paths.append(libsvm_path)

    model_paths = []
    for libsvm_path in libsvm_paths:
        if adversarial:
            lines_0 = []
            lines_minus_1 = []
            with open(libsvm_path) as f:
                for line in f:
                    lines_0.append(line.replace('1   ', '0   ', 1))
                    lines_minus_1.append(line.replace('1   ', '-1   ', 1))
            with open(libsvm_path, 'a') as f:
                for line in lines_0:
                    f.write(line)
                for line in lines_minus_1:
                    f.write(line)
        user = libsvm_path.split('/')[-2]
        os.system('mkdir -p {0}/model/{1}'.format(dataset_dir, user))
        model_path = os.path.join(dataset_dir, 'model', user, '.'.join([user, 'model']))
        # TODO tune the params
        if n_classes == 1:
            os.system('{2}/svm-train '
                      '-s 2 -t 2 -g 1 -h 1  '
                      '{0} {1}\n'.format(libsvm_path, model_path, BIN_ROOT))
        elif n_classes == 2:
            os.system('{2}/svm-train '
                      '-s 0 -t 2 -g 0.5 -r 0 -c 5000 -h 1 -q '
                      '{0} {1}\n'.format(libsvm_path, model_path, BIN_ROOT))
        else:
            raise NotImplementedError('{0}-class svm has not implemented'.format(n_classes))
        if model_path not in model_paths:
            model_paths.append(model_path)

    return model_paths


def predict(dataset_dir, model_paths, testing_filepaths):
    """
    predict using svm models

    :param model_paths: paths to models
    :param testing_filepaths: paths to testing files
    :return: accuracy list like ['model:user.model:test:user.test_data.arff.libsvm:accuracy:0%']
    """
    # format to arff and then to libsvm
    libsvm_paths = []
    for filepath in testing_filepaths:
        os.system('{1}/make_arff.exe '
                  '{0} 1 1 > {0}.arff'.format(filepath, BIN_ROOT))
        os.system("sed -i \"s/\-nan/0/g\" {0}.arff".format(filepath))

        user = filepath.split('/')[-2]
        os.system('mkdir -p {0}'.format(os.path.join(dataset_dir, TEST, user)))
        libsvm_path = os.path.join(dataset_dir, TEST, user,
                                   '.'.join([user, os.path.basename(filepath), 'arff', 'libsvm']))

        os.system('python {2}/arff2libsvm.py {0}.arff {1}'.format(filepath, libsvm_path, BIN_ROOT))
        if libsvm_path not in libsvm_paths:
            libsvm_paths.append(libsvm_path)

    # get accuracy
    accuracies = []
    for model_path in model_paths:
        for libsvm_path in libsvm_paths:
            os.system('{3}/svm-predict '
                      '{0} {1} {2}'.format(libsvm_path, model_path, '/tmp/output_file', BIN_ROOT))
            with open('/tmp/output_file') as f:
                accuracy = f.readlines()[-1].split(' ')[2]
                accuracies.append('model:{0}:test:{1}:accuracy:{2}'.format(
                    os.path.basename(model_path), os.path.basename(libsvm_path), accuracy))
    return accuracies


if __name__ == '__main__':
    root = '/home/cyrus/Public/RiskCog'
    BIN_ROOT = os.path.join(root, 'server/riskserver-debugging-svm-with-queue/bin')
    log_path = os.path.join(root, 'results/one_class_svm_log')

    dataset_dirs = []
    for root_, dir_, file_ in os.walk(os.path.join(root, 'dataset/mimicry_raw')):
        if TRAIN in dir_:
            dataset_dirs.append(root_)
    print '>> test examples {0} in total'.format(len(dataset_dirs))

    for dataset_dir in dataset_dirs:
        state = dataset_dir.split('/')[-2]
        test_name = dataset_dir.split('/')[-1]
        # preprocessing, training, predicting
        training_set, _, testing_set, _ = preprocessing(dataset_dir)
        model_paths = train(dataset_dir, training_set, [], n_classes=2, adversarial=True)

        accuracies_1 = predict(dataset_dir, model_paths, training_set)
        accuracies_2 = predict(dataset_dir, model_paths, testing_set)

        # log gen
        os.system('rm {0}'.format(log_path))
        for accuracy in accuracies_1 + accuracies_2:
            with open(log_path, 'a') as f:
                f.write(accuracy)
                f.write('\n')

        # log parse
        logs = np.loadtxt(log_path, delimiter=':', dtype=np.string_)
        logs = logs[:, (1, 3, 5)]

        statistics = [[], []]
        for log in logs:
            if log[0].split('.')[0] == log[1].split('.')[0]:
                statistics[0].append(float(log[2][:-1]))
            else:
                statistics[1].append(float(log[2][:-1]))
        result = [np.mean(statistics[0]), np.mean(statistics[1])]
        print '>> state:{0}:test_name:{1}:self_accuracy:{2}:other_accuracy:{3}'.format(
            state, test_name, result[0], result[1])
