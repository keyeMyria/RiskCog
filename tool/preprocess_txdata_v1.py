# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
import random
import sys
import time

import eqerr_check

import numpy as np

from multiprocessing import Pool

import tensorflow as tf

# Set some parameters can be modified.
class Config(object):

	def __init__(self, windowSize):
		self.interval_Len = int(windowSize)
		self.TH = 0.7

		self.tmpSourcePath = "./rawTxData_" + windowSize
		self.destinePath = "./txData_tfRecord_" + windowSize
		self.rawPath = "/home/linzi/txdata/largeScale_Test_TX_LSTM/rawData"

		self.trainRatio = 0.8
		self.fileNum = 1000
		self.processesNum = 10
		self.perShardNum = 100
		self.randomSeed = 0
		self.classNum = 10

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

# Return a mark list, value '1' means the corresponding 9-element tuple is invalid, value '0' means opposite.
def checkZeroAndOutlier(data):
	upLimit = [30.0, 30.0, 30.0, 6.0, 6.0, 6.0, 30.0, 30.0, 30.0]
	downLimit = [-30.0, -30.0, -30.0, -6.0, -6.0, -6.0, -30.0, -30.0, -30.0]
	mark = []
	for i in range(int(len(data) / 9)):
		mark.append(0)

	eps = 0.0000000001

	for i in range(len(mark)):

		acc_rept_x = data[i * 9] - data[i * 9 + 6]
		acc_rept_y = data[i * 9 + 1] - data[i * 9 + 7]
		acc_rept_z = data[i * 9 + 2] - data[i * 9 + 8]
		acc_rept = math.sqrt(acc_rept_x * acc_rept_x + acc_rept_y * acc_rept_y + acc_rept_z * acc_rept_z)

		if acc_rept >= 0.6:
			mark[i] = 1
			continue

		# Smart phone is placed vertically
		if abs(data[i * 9 + 6]) < 1.5 and abs(data[i * 9 + 7]) < 1.5 and abs(data[i * 9 + 8]) > 9.0:
			mark[i] = 1
			continue

		# Smart phone can shoot the face of user
		if abs(data[i * 9 + 6]) >= 7.07 or data[i * 9 + 7] <= 0 or data[i * 9 + 7] >= 10 or data[i * 9 + 8] <= 0 or data[i * 9 + 8] >= 10:
			mark[i] = 1
			continue

		# All gyroscope values (x, y, z) are equal to zero
		if abs(data[i * 9 + 3]) < eps and abs(data[i * 9 + 4]) < eps and abs(data[i * 9 + 5]) < eps :
			mark[i] = 1
			continue

		# One of the value in a 9-element tuple is beyond prescribed boundary
		for j in range(9):
			if data[i * 9 + j] > upLimit[j] or data[i * 9 + j] < downLimit[j]:
				mark[i] = 1
				break

		if mark[i] == 1:
			continue

		# Normalization
		# for j in range(9):
		# 	data[i * 9 + j] =  2.0 * (data[i * 9 + j] - downLimit[j]) / (upLimit[j] - downLimit[j]) - 1.0

	return mark


# 获取连续数据段(长度大于指定参数interval)
def getInterval(groupNum, markArray, intervalLen):
	st = 0
	res = []
	while st < groupNum:
		while st < groupNum and markArray[st] != 0:
			st = st + 1
		end = st
		while end < groupNum and markArray[end] == 0:
			end = end + 1
		if end - st < intervalLen:
			st = end
			continue
		interval = {}
		interval['left'] = st
		interval['right'] = end - 1

		res.append(interval)
		st = end

	return res

def createDir(path):
	if os.path.isdir(path):
		pass
	else:
		os.makedirs(path)

def dataSplit(sourcePath, interval_Len, class_id, user):
	config = Config(str(interval_Len))

	fileList = getFileList(sourcePath)
	windowList = []

	for myFile in fileList:

		# Get raw data
		rawData = []
		with open(os.path.join(sourcePath, myFile), 'r') as f:
			for line in f:
				rawData.append(float(line))

		# Eliminate zero and other abnormal data
		mark_1 = checkZeroAndOutlier(rawData)
		groupNum = len(mark_1)

		# All valid successive data sequences
		intervalList = getInterval(groupNum, mark_1, interval_Len)

		if intervalList == []:
			continue

		res = intervalList
		# 对每个合法序列做滑动窗处理
		count = 0
		for i in range(len(res)):
			st = res[i]['left']
			end = res[i]['right']
			while end - st + 1 >= interval_Len:
				tmpList = []
				head = st
				tail = st + interval_Len

				tmp = rawData[head * 9 : tail * 9]

				for j in range(interval_Len):
					acc_rept_x = data[j * 9] - data[j * 9 + 6]
					acc_rept_y = data[j * 9 + 1] - data[j * 9 + 7]
					acc_rept_z = data[j * 9 + 2] - data[j * 9 + 8]
					acc_rept = math.sqrt(acc_rept_x * acc_rept_x + acc_rept_y * acc_rept_y + acc_rept_z * acc_rept_z)
					r = math.sqrt(data[j * 9 + 6] * data[j * 9 + 6] + data[j * 9 + 7] * data[j * 9 + 7] + data[j * 9 + 8] * data[j * 9 + 8])
					theta = math.acos(data[j * 9 + 8] / r)
					phi = math.atan(data[j * 9 + 7] / data[j * 9 + 6])
					tmpList = tmpList + tmp[j * 9 : (j + 1) * 9] + [acc_rept, r, phi, theta]

				tmp = []
				tmp.append(tmpList)
				tmp.append(class_id)
				windowList.append(tmp)
				# windowList.append(tmpList)
				##

				st = st + 1

	return windowList

def stripEqerr(windowSize):
	
	config = Config(windowSize)

	dirList = getFileList(config.tmpSourcePath)
	count = 1

	for myDir in dirList:
		fileList = getFileList(os.path.join(config.tmpSourcePath, myDir))
		print(str(count) + "  " + myDir)

		for myFile in fileList:
			res = eqerr_check.isEqualError(os.path.join(config.tmpSourcePath, myDir, myFile), config.TH)
			#print res
			if res == 1:
				os.system("rm {}".format(os.path.join(config.tmpSourcePath, myDir, myFile)))
				print("-remove " + os.path.join(myDir, myFile))

		print("")

		count = count + 1

def _real_write(windowList, split_name, shard_id, destinePath):

	output_filename = os.path.join(destinePath, split_name, "riskcog_" + split_name + "_" + str(shard_id) + ".tfrecord")

	with tf.python_io.TFRecordWriter(output_filename) as tfrecord_writer:
		for i in range(len(windowList)):

			window_data = windowList[i][0]
			class_id = windowList[i][1]

			example = tf.train.Example(features=tf.train.Features(
				feature={
					'window/encoded': _float_feature(window_data),
					'window/label': _int64_feature(class_id),
				}))
			tfrecord_writer.write(example.SerializeToString())


def dataPreprocess(windowSize):
	
	config = Config(windowSize)

	dirList = getFileList(config.tmpSourcePath)
	count = 0

	os.system("rm -rf {}".format(config.destinePath))
	createDir(config.destinePath)
	createDir(os.path.join(config.destinePath, "train"))
	createDir(os.path.join(config.destinePath, "test"))

	dataSet_train = []
	dataSet_test = []

	pool = Pool(processes = config.processesNum)
	shard_id_train = 0
	shard_id_test = 0
	totalClass = 0

	for myDir in dirList:

		# createDir(os.path.join(config.destinePath, myDir))
		preprocessed_dataSet = dataSplit(os.path.join(config.tmpSourcePath, myDir), config.interval_Len, count, myDir)
		print(str(count) + "  " + myDir + " " + str(len(preprocessed_dataSet)) + "  OK")
		count = count + 1

		##
		# with open("./windowNum.txt", "a+") as f:
		# 	f.write(str(len(preprocessed_dataSet)) + "\n")
		##

		if len(preprocessed_dataSet) < config.fileNum:
			continue

		totalClass = totalClass + 1

		random.seed(config.randomSeed)
		random.shuffle(preprocessed_dataSet)
		preprocessed_dataSet = preprocessed_dataSet[ : config.fileNum]

		# index = 0
		# for item in preprocessed_dataSet:
		# 	with open(os.path.join(config.destinePath, myDir, "sample75_" + str(index) + ".txt"), "a+") as f:
		# 		for i in range(len(item)):
		# 			f.write(str(item[i]) + "\n")
		# 	index = index + 1
		dataSet_train = dataSet_train + preprocessed_dataSet[ : int(config.trainRatio * config.fileNum)]
		dataSet_test = dataSet_test + preprocessed_dataSet[int(config.trainRatio * config.fileNum) : ]

		while len(dataSet_train) >= config.perShardNum:
			tmpTrainSet = dataSet_train[ : config.perShardNum]
			dataSet_train = dataSet_train[config.perShardNum : ]
			pool.apply_async(_real_write, args = (tmpTrainSet, "train", shard_id_train, config.destinePath))
			shard_id_train = shard_id_train + 1

		while len(dataSet_test) >= config.perShardNum:
			tmpTestSet = dataSet_test[ : config.perShardNum]
			dataSet_test = dataSet_test[config.perShardNum : ]
			pool.apply_async(_real_write, args = (tmpTestSet, "test", shard_id_test, config.destinePath))
			shard_id_test = shard_id_test + 1

		if totalClass >= config.classNum:
			break

	if len(dataSet_train) > 0:
		pool.apply_async(_real_write, args = (dataSet_train, "train", shard_id_train, config.destinePath))

	if len(dataSet_test) > 0:
		pool.apply_async(_real_write, args = (dataSet_test, "test", shard_id_test, config.destinePath))

	pool.close()
	pool.join()	
	print("Total Class Num : " + str(totalClass))

def infoRecord(windowSize):
	config = Config(windowSize)

	dirList = getFileList(config.destinePath)
	userInfo = []

	for user in dirList:
		fileList = getFileList(os.path.join(config.destinePath, user))
		tmp = []
		tmp.append(len(fileList))
		tmp.append(user)
		userInfo.append(tmp)

	userInfo.sort(reverse = True)
	userList = []
	content = ""
	for i in range(len(userInfo)):
		content = content + userInfo[i][1] + "  " + str(userInfo[i][0]) + "\n"
		userList.append(userInfo[i][0])

	with open("./validDataNum_" + windowSize + ".txt", "a+") as f:
		f.write(content)
			
if __name__ == '__main__':
	time_start = time.time()
	
	windowSize = sys.argv[1]
	windowSize = windowSize.rstrip("\n")
	windowSize = windowSize.rstrip("\r")
	config = Config(windowSize)

	os.system("cp -r {0} {1}".format(config.rawPath, config.tmpSourcePath))

	stripEqerr(windowSize)

	dataPreprocess(windowSize)

	time_end = time.time()

	print("Total Time Used : ", time_end - time_start)

#	infoRecord(windowSize)

	os.system("rm -rf {}".format(config.tmpSourcePath))
