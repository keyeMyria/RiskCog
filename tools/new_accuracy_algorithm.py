# -*- coding=utf-8 -*-

# 新accuracy算法
# 输入 阈值 prediction原文件（n^2）
# 输出 新旧accuracy的对比图

import os

# full path please
import tools

TARGET_FILE = ''
# full path please
RESULT_DIR = '/home/cyrus/Desktop/MyInternshipProject/WeekSummary/6/new accuracy algorithm/tx_130'
threshold = 0.3


def getNewAccuracy(file_, threshhold):
    file_name = os.path.join(RESULT_DIR, file_)
    prediction = []
    with open(file_name) as f:
        lines = f.readlines()
        # remove head and tail
        lines.remove(lines[0])
        lines.pop()
        # get all prediction
        for line in lines:
            t = line.split(' ')
            prediction.append(float(t[1]))

        # get all parameter
        m = 0 # number of prediction > threshold
        n = 0 # number of prediction < threshold
        for i in prediction:
            if i >= threshhold:
                m += 1
            else:
                n += 1
        print '# m', m, 'n', n


        # calculate new accuracy
        # when n or m == 1, there is no available i, j
        if m == 0 and n == 0:
            return 0.0, 0.0
        if m == 1 or n == 1 or m == 0 or n == 0:
            new_accuracy = 1.0 - 1.0/(m+n)
            old_accuracy = 1.0 - 1.0/(m+n)
            return new_accuracy, old_accuracy

        if m >= n:
            for i in range(0, n):
                for j in range(0, m):
                    if 2*i > n or i+j < n or 2*j >= m:
                        continue
                    else:
                        if i == 0:
                            continue
                        new_accuracy = (m-j)/float(m-j+i)
                        old_accuracy = m/float(n+m)
                        print '# info', i, n-i, j, m-j, (m-j)/float(m-j+i), old_accuracy
                        return new_accuracy, old_accuracy
        else:
            for i in range(n, 0, -1):
                for j in range(m, 0, -1):
                    if 2*i <= n or i+j > n or 2*j < m:
                        continue
                    else:
                        new_accuracy = (m-j)/float(m-j+i)
                        old_accuracy = m/float(n+m)
                        print '# info', i, n-i, j, m-j, (m-j)/float(m-j+i), old_accuracy
                        return new_accuracy, old_accuracy

        print '# 无解'
        new_accuracy = 1.0 - 1.0/(m+n)
        old_accuracy = 1.0 - 1.0/(m+n)
        return new_accuracy, old_accuracy


if __name__ == '__main__':
    files = os.listdir(RESULT_DIR)
    new = []
    old = []
    for file_ in files:
        print '\n# current file is', file_
        new_accuracy, old_accuracy = getNewAccuracy(file_, threshold)
        new.append(new_accuracy)
        old.append(old_accuracy)

    new = tools.getSorted(new)
    old = tools.getSorted(old)
    START = 0
    STOP = len(new)
    tools.plotSimplePlot(old[START:STOP], new[START:STOP],
                         xlegend='old', ylegend='new',
                         xlabel='test id', ylabel='accuracy',
                         title='cross check ant financial '+str(threshold))