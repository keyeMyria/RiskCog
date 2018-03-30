# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
from multiprocessing import Pool

import numpy as np
import tensorflow as tf


# Set some parameters can be modified.
class Config(object):
    def __init__(self):
        self.intervalLen = 68
        self.originalLen = 128
        self.overlap = 0.5

        self.sourcePath = "../dataset/UCI_HAR_Dataset"
        self.destinePath = "../dataset/UCI_TFRecord"
        self.destinePath_DFT = "../dataset/UCI_DFT_TFRecord"

        self.processesNum = 2
        self.perShardNum = 400
        self.randomSeed = 0

        self.fileType = ['body_gyro_x_', 'body_gyro_y_', 'body_gyro_z_', 'total_acc_x_', 'total_acc_y_', 'total_acc_z_',
                         'body_acc_x_', 'body_acc_y_', 'body_acc_z_']
        self.orderTable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 3, 5, 7, 9, 2, 4, 6, 8, 1, 4, 7, 1, 5, 8, 2, 5, 9, 3, 6, 9, 4,
                           8, 3, 7, 2, 6]


def _float_feature(values):
    """Returns a TF-Feature of floats.
    Args:
      values: A scalar of list of values.
    Returns:
      A TF-Feature.
    """
    if not isinstance(values, (tuple, list)):
        values = [values]
    return tf.train.Feature(float_list=tf.train.FloatList(value=values))


def _int64_feature(values):
    """Returns a TF-Feature of int64s.
    Args:
      values: A scalar or list of values.
    Returns:
      A TF-Feature.
    """
    if not isinstance(values, (tuple, list)):
        values = [values]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=values))


# 获取path对应文件夹下的所有目录和文件名
def getFileList(path):
    fileList = []
    for myFile in os.listdir(path):
        fileList.append(myFile)
    return fileList


def createDir(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)


def _real_write(windowList, split_name, shard_id, destinePath):
    output_filename = os.path.join(destinePath, split_name, "UCI_" + split_name + "_" + str(shard_id) + ".tfrecord")

    with tf.python_io.TFRecordWriter(output_filename) as tfrecord_writer:
        for i in range(len(windowList)):
            window_data = windowList[i][0]
            class_id = windowList[i][1]

            # print(window_data)
            # print("")
            # print(class_id)

            example = tf.train.Example(features=tf.train.Features(
                feature={
                    'window/encoded': _float_feature(window_data),
                    'window/label': _int64_feature(class_id),
                }))
            tfrecord_writer.write(example.SerializeToString())


def mergeData(dataType):
    config = Config()

    originalLabel = []
    originalDataSet = [[], [], [], [], [], [], [], [], []]

    with open(os.path.join(config.sourcePath, dataType, "y_" + dataType + ".txt"), "r") as f:
        for line in f:
            originalLabel.append(int(line))

    for i in range(9):
        with open(os.path.join(config.sourcePath, dataType, "Inertial_Signals", config.fileType[i] + dataType + ".txt"),
                  "r") as f:
            for line in f:
                originalDataSet[i].append(line)

    label = []
    dataSet = [[], [], [], [], [], [], [], [], []]
    st = 0
    while True:
        end = st + 1
        while end < len(originalLabel) and originalLabel[end] == originalLabel[st]:
            end = end + 1

        label.append(originalLabel[st])

        for i in range(9):
            tmpList = originalDataSet[i][st: end]
            tmpDataList = tmpList[0].split()

            for j in range(end - st - 1):
                tmp = tmpList[j + 1].split()
                tmpDataList = tmpDataList + tmp[64:]

            for j in range(len(tmpDataList)):
                tmpDataList[j] = float(tmpDataList[j])

            dataSet[i].append(tmpDataList)

        st = end
        if st >= len(originalLabel):
            break

    return dataSet, label


def convert_to_tfRecord(dataType, dataSet, label):
    config = Config()
    pool = Pool(processes=config.processesNum)
    signalImageList = []
    activityImageList = []
    shard_id_signal = 0
    shard_id_activity = 0

    for i in range(len(label)):
        st = 0
        end = len(dataSet[0][i]) - 1
        while end - st + 1 >= config.intervalLen:
            tmp = []
            for j in range(len(config.orderTable)):
                tmp = tmp + dataSet[config.orderTable[j] - 1][i][st: st + config.intervalLen]

            tmpSignal = []
            tmpSignal.append(tmp)
            tmpSignal.append(label[i])
            signalImageList.append(tmpSignal)

            signalImage = np.reshape(tmp, (36, -1))
            activityImage = np.fft.fft2(signalImage)
            tmpActivity = []
            tmpActivity.append(np.reshape(np.abs(activityImage), (1, -1)).tolist()[0])
            tmpActivity.append(label[i])
            activityImageList.append(tmpActivity)

            st = st + int(config.overlap * config.intervalLen)

        while len(signalImageList) >= config.perShardNum:
            tmpSignalList = signalImageList[: config.perShardNum]
            signalImageList = signalImageList[config.perShardNum:]
            pool.apply_async(_real_write, args=(tmpSignalList, dataType, shard_id_signal, config.destinePath))
            shard_id_signal = shard_id_signal + 1

        while len(activityImageList) >= config.perShardNum:
            tmpActivityList = activityImageList[: config.perShardNum]
            activityImageList = activityImageList[config.perShardNum:]
            pool.apply_async(_real_write, args=(tmpActivityList, dataType, shard_id_activity, config.destinePath_DFT))
            shard_id_activity = shard_id_activity + 1

    if len(signalImageList) > 0:
        pool.apply_async(_real_write, args=(signalImageList, dataType, shard_id_signal, config.destinePath))

    if len(activityImageList) > 0:
        pool.apply_async(_real_write, args=(activityImageList, dataType, shard_id_activity, config.destinePath_DFT))

    pool.close()
    pool.join()


def dataPreprocess():
    config = Config()

    dataSetTrain, labelTrain = mergeData("train")
    dataSetTest, labelTest = mergeData("test")

    os.system("rm -rf {}".format(config.destinePath))
    createDir(config.destinePath)
    createDir(os.path.join(config.destinePath, "train"))
    createDir(os.path.join(config.destinePath, "test"))

    os.system("rm -rf {}".format(config.destinePath_DFT))
    createDir(config.destinePath_DFT)
    createDir(os.path.join(config.destinePath_DFT, "train"))
    createDir(os.path.join(config.destinePath_DFT, "test"))

    convert_to_tfRecord("train", dataSetTrain, labelTrain)
    convert_to_tfRecord("test", dataSetTest, labelTest)


if __name__ == '__main__':
    time_start = time.time()

    dataPreprocess()

    time_end = time.time()

    print("Total Time Used : ", time_end - time_start)
