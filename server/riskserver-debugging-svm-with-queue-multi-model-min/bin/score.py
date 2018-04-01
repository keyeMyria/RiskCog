'compute metrics for libsvm test file and VW/Liblinear predictions file'

import numpy as np
from sklearn.metrics import accuracy_score as accuracy
from sklearn.metrics import precision_score as precision
from sklearn.metrics import recall_score as recall


def get_accuracy(y_file, p_file):
    print '## TRACE ##', 'computing accuracy for', y_file, p_file
    p = np.loadtxt(p_file)

    y_predicted = np.ones((p.shape[0]))
    y_predicted[p < 0] = -1

    y = np.loadtxt(y_file, usecols=[0])

    if len(y) == 0 or len(y_predicted) == 0:
        return 0.0

    res = accuracy(y, y_predicted)

    if res == 1.0:
        print y, y_predicted

    return res


def get_precision(y_file, p_file):
    print '## TRACE ##', 'computing precision for', y_file, p_file
    p = np.loadtxt(p_file)

    y_predicted = np.ones((p.shape[0]))
    y_predicted[p < 0] = -1

    y = np.loadtxt(y_file, usecols=[0])

    if len(y) == 0 or len(y_predicted) == 0:
        return 0.0

    return precision(y, y_predicted)


def get_recall(y_file, p_file):
    print '## TRACE ##', 'computing recall for', y_file, p_file
    p = np.loadtxt(p_file)

    y_predicted = np.ones((p.shape[0]))
    y_predicted[p < 0] = -1

    y = np.loadtxt(y_file, usecols=[0])

    if len(y) == 0 or len(y_predicted) == 0:
        return 0.0

    return recall(y, y_predicted)


def get_result(file_name):
    fp = open(file_name, 'r')
    lines = [x.strip() for x in fp.readlines() if x.startswith("-1") or x.startswith("1")]
    if len(lines) == 0:
        return 0, 0, 0
    lines.pop()
    fp.close()

    TP, FP, TN, FN = 0, 0, 0, 0
    for line in lines:
        if line.startswith('1'):
            if line.endswith('1'):
                TP = TP + 1
            else:
                FP = FP + 1
        else:
            if line.endswith('1'):
                FN = FN + 1
            else:
                TN = TN + 1

    if TP + FP == 0:
        Powner = 0
    else:
        Powner = TP * 1.0 / (TP + FP)

    if TP + FN == 0:
        Rowner = 0
    else:
        Rowner = TP * 1.0 / (TP + FN)

    if TN + FN == 0:
        Pother = 0
    else:
        Pother = TN * 1.0 / (TN + FN)

    if TN + FP == 0:
        Rother = 0
    else:
        Rother = TN * 1.0 / (TN + FP)
    Accuracy = (TP + TN) * 1.0 / (TP + FP + FN + TN)

    return Accuracy, Powner, Rowner
