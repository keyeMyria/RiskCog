#!/usr/bin/env python

'compute metrics for libsvm test file and VW/Liblinear predictions file'

import sys

import numpy as np

# configure numpy to raise warnings as exceptions
np.seterr(all='raise')
from sklearn.metrics import accuracy_score as accuracy
from sklearn.metrics import precision_score as precision
from sklearn.metrics import recall_score as recall
from sklearn.metrics import roc_auc_score as AUC
from sklearn.metrics import confusion_matrix


def compute_score(y_file, p_file, summary_file, extras={}):
    print "loading p..."

    try:
        p = np.loadtxt(p_file)
    except Exception as e:
        print e
        print "skipping prediciton for user: %s" % extras['imei']
        return (0, 0, 0, 0, [[0, 0], [0, 0]])

    y_predicted = np.ones((p.shape[0]))
    y_predicted[p < 0] = -1

    print "loading y..."

    try:
        y = np.loadtxt(y_file, usecols=[0])
    except Exception as e:
        print e
        print "skipping prediciton for user: %s" % extras['imei']
        return (0, 0, 0, 0, [[0, 0], [0, 0]])

    try:
        acc = accuracy(y, y_predicted)
        prec = precision(y, y_predicted, average='binary')
        reca = recall(y, y_predicted, average='binary')
        auc = AUC(y, p)
        cm = confusion_matrix(y, y_predicted)
    except FloatingPointError as fpe:
        print fpe
        print "skipping accuracy, precision, recall, AUC & confusion matrix due to floating point error"
        return (0, 0, 0, 0, [[0, 0], [0, 0]])
    except Exception as e:
        print e
        print "skipping user: {} due to error when computing metrics.".format(extras['imei'])
        return (0, 0, 0, 0, [[0, 0], [0, 0]])

    with open(summary_file, 'w') as w:
        with open(summary_file[:-4] + '.csv', 'w') as c:
            print "accuracy:", acc
            w.write("accuracy: " + str(acc) + '\n')
            print "precision:", prec
            w.write("precision: " + str(prec) + '\n')
            print "recall:", reca
            w.write("recall: " + str(reca) + '\n')
            print "AUC:", auc
            w.write("AUC: " + str(auc) + '\n')

            csv_items = []
            for k in extras:
                csv_items.append(str(extras[k]))

            # add the accuracy, precision & recall
            csv_items = csv_items + [str(acc), str(prec), str(reca)]

            c.write(",".join(csv_items) + "\n")

            print
            print "confusion matrix:"
            print cm
            w.write("confusion matrix: " + str(cm) + '\n')

    return acc, prec, reca, auc, cm


if __name__ == "__main__":
    compute_score(sys.argv[1], sys.argv[2], sys.argv[3])

"""
run score.py data/test_v.txt vw/p_v_logistic.txt

accuracy: 0.994675826535
i
confusion matrix:
[[27444   136]
 [  236 42054]]

AUC: 0.998418419401
"""

"""
p_v_hinge.txt

accuracy: 0.993502218406

confusion matrix:
[[27310   270]
 [  184 42106]]

AUC: 0.99632599445
"""

"""
cdblock

accuracy: 0.993244597109
AUC: 0.993511427279

confusion matrix:
[[27436   144]
 [  328 41962]]
"""

"""
cdblock -s 7 (logistic regression)
accuracy: 0.985201087734
AUC: 0.985763288671

confusion matrix:
[[27261   319]
 [  715 41575]]
"""

"""
score_streamsvm.py (hinge)

accuracy: 0.990596822671
AUC: 0.991292619197

confusion matrix:
[[27431   149]
 [  508 41782]]
 

(ui) 
accuracy: 0.990596822671
AUC: 0.998972438313

confusion matrix:
[[27431   149]
 [  508 41782]]
 
"""
