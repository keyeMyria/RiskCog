"""
plot the curves of accuracy of train or test

Usage:
    python plot.py path

Return:
    save a png file named after the path

Args:
    root: log path

Author:
    Qiang Liu
"""


import matplotlib.pyplot as plt
import sys
import numpy as np
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Usage: python {0}'.format(sys.argv[0])
        exit(-1)

    path = sys.argv[-1]

    offline = {'train_iter':[], 'train_acc':[], 'others_acc':[]}
    # online = {'model':None, train_iter:[], train_acc:[], others_acc:[]}
    with open(path) as f:
        for line in f.readlines():
            if line.startswith('train_iter'):
                # print line
                # traing_iter:0:train_accy:0.36:loss:2.68:others_acc:0.87:loss:3.30
                tmp = line.split(':')
                offline['train_iter'].append(int(tmp[1]))
                offline['train_acc'].append(float(tmp[3]))
                offline['others_acc'].append(float(tmp[7]))
            elif line.startswith('best_epoches'):
                # best_epoch:0:best_accuracy:0.36:best_others_acc:0.87
                pass
            else:
                pass

    plt.figure()
    ax = plt.subplot(111)
    x = np.arange(len(offline['train_iter']))
    ax.plot(x, offline['train_acc'],  "b--",  label="Offline Train Accuracy")
    ax.plot(x, offline['others_acc'],  "g--",  label="Offline Other Accuracy")
    # comment on axes
    # plt.xlabel('iter')
    # plt.ylabel('accuracy')
    # range of axes
    ax.axis([0, len(x), min(offline['train_acc']), 1]) # x_min, x_max, y_min, y_max
    ax.xaxis.set_major_locator(MultipleLocator(len(x)/10)) # interval of x axis
    plt.title("Training session's progress over iterations")
    plt.legend(loc='center right', shadow=True)
    # plt.show()
    plt.savefig(path)
    print 'save to {0}.png'.format(path)
    plt.close()
