import os

# import pywt
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import seaborn as sns
from scipy import signal
from scipy.signal import filter_design as fd
from sklearn import preprocessing as pp

import constant


def getFilelists(training_log_dir):
    nnSitFilelist = []
    nnWalkFilelist = []
    svmSitFilelist = []
    svmWalkFilelist = []

    filenames = os.listdir(training_log_dir)
    for filename in filenames:
        t = filename.split('_')
        if t[0] == constant.NAMEnn:
            if t[1] == 'nn':
                if t[3] == 'sit':
                    nnSitFilelist.append(filename)
                else:
                    nnWalkFilelist.append(filename)
        elif t[0] == constant.NAMEsvm:
            if t[3] == 'sit':
                svmSitFilelist.append(filename)
            else:
                svmWalkFilelist.append(filename)
    return nnSitFilelist, nnWalkFilelist, svmSitFilelist, svmWalkFilelist


def getFileNumbers(filename):
    t = filename.split('_')
    return t[2]


def getRunningTime(filename):
    with open(os.path.join(constant.TRAIN_LOG_DIR, filename)) as f:
        firstline = f.readlines(0)
    t = firstline[0].split(' ')
    return float(t[2]) / 1000


def getDataLists(a1, a2, b1, b2):
    nnSitFileNumbers = []
    nnWalkFileNumbers = []
    nnSitRunningTime = []
    nnWalkRunningTime = []
    svmSitFileNumbers = []
    svmWalkFileNumbers = []
    svmSitRunningTime = []
    svmWalkRunningTime = []
    for file in a1:
        nnSitFileNumbers.append(getFileNumbers(file))
        nnSitRunningTime.append(getRunningTime(file))
    for file in a2:
        nnWalkFileNumbers.append(getFileNumbers(file))
        nnWalkRunningTime.append(getRunningTime(file))
    for file in b1:
        svmSitFileNumbers.append(getFileNumbers(file))
        svmSitRunningTime.append(getRunningTime(file))
    for file in b2:
        svmWalkFileNumbers.append(getFileNumbers(file))
        svmWalkRunningTime.append(getRunningTime(file))

    return nnSitFileNumbers, nnSitRunningTime, nnWalkFileNumbers, nnWalkRunningTime, \
           svmSitFileNumbers, svmSitRunningTime, svmWalkFileNumbers, svmWalkRunningTime


def getSensorData(path, *sensor):
    """
    Input the sensor data in standard format and split them into lists.
    Tell the sensor or sensors you want with a list. What you can use are
    'acceleration', 'gyroscope' and 'gravity'.

    :param path: full path of the file containing sensor data
    :param sensor: the sensor or sensors you want
    :return: dict for sensor data
    """

    with open(path) as f:
        lines = f.readlines()
        f.close()

        acceleration = [[], [], []]
        gravity = [[], [], []]
        gyroscope = [[], [], []]

        for i in range(0, len(lines), 9):
            if 'acceleration' in sensor:
                acceleration[0].append(lines[i + 0])
                acceleration[1].append(lines[i + 1])
                acceleration[2].append(lines[i + 2])
            if 'gyroscope' in sensor:
                gyroscope[0].append(lines[i + 3])
                gyroscope[1].append(lines[i + 4])
                gyroscope[2].append(lines[i + 5])
            if 'gravity' in sensor:
                gravity[0].append(lines[i + 6])
                gravity[1].append(lines[i + 7])
                gravity[2].append(lines[i + 8])

    sensor_data = {}
    if 'acceleration' in sensor:
        sensor_data['acceleration'] = acceleration
    if 'gyroscope' in sensor:
        sensor_data['gyroscope'] = gyroscope
    if 'gravity' in sensor:
        sensor_data['gravity'] = gravity
    return sensor_data



def updateGyroscope(dir, name):
    path = os.path.join(dir, name)
    with open(path) as f:
        lines = f.readlines()
        f.close()

        gyx = []
        gyy = []
        gyz = []

        for i in range(0, len(lines), 9):
            gyx.append(lines[i + 3])
            gyy.append(lines[i + 4])
            gyz.append(lines[i + 5])

        gyx = [float(x) for x in gyx]
        gyy = [float(y) for y in gyy]
        gyz = [float(z) for z in gyz]

        gyx_hpf = getHPF(1, [gyx])[0]
        gyy_hpf = getHPF(1, [gyy])[0]
        gyz_hpf = getHPF(1, [gyz])[0]

        gyx_hpf = [str(x) + '\n' for x in gyx_hpf]
        gyy_hpf = [str(y) + '\n' for y in gyy_hpf]
        gyz_hpf = [str(z) + '\n' for z in gyz_hpf]

        print len(gyx)
        print len(lines)
        print len(gyx_hpf)

        for i in range(0, len(gyx_hpf)):
            lines[i * 9 + 3] = gyx_hpf[i]
            lines[i * 9 + 4] = gyy_hpf[i]
            lines[i * 9 + 5] = gyz_hpf[i]

    with open(os.path.join(dir, '..', 'train_hpf', name), 'w') as r:
        r.writelines(lines)
        r.close()


def getShapiroWilk(x):
    return stats.shapiro(x)[1]


def getMean(x):
    array = np.array(x)
    return np.mean(array)


def getStd(x):
    return np.std(x)


def getVar(x):
    array = np.array(x)
    return np.var(array)


def getMedian(x):
    return np.median(x)


def getMode(x):
    t = stats.mode(x)
    return str(t[0][0]) + '(' + str(t[1][0]) + '/' + str(len(x)) + ')'


def getPTP(x):
    return np.ptp(x)


def getZScore(data, mean, std):
    return (data - mean) / std


def plotVarAcc(datas, accuracy, r=False):
    x = [datas[i][0] for i in range(0, len(datas))]
    y = [datas[i][1] for i in range(0, len(datas))]
    z = [datas[i][2] for i in range(0, len(datas))]
    if r:
        plt.figure(2)
        plt.subplot(311)
        plt.grid(True)
        plt.plot(x, accuracy, 'r^')
        plt.subplot(312)
        plt.grid(True)
        plt.plot(y, accuracy, 'r^')
        plt.subplot(313)
        plt.grid(True)
        plt.plot(z, accuracy, 'r^')
        plt.show()
    else:
        plt.figure(2)
        plt.subplot(311)
        plt.grid(True)
        plt.plot(x, 'r^')
        plt.subplot(312)
        plt.grid(True)
        plt.plot(y)
        plt.subplot(313)
        plt.grid(True)
        plt.plot(z)
        plt.subplot(311)
        plt.plot(accuracy)
        plt.subplot(312)
        plt.plot(accuracy)
        plt.subplot(313)
        plt.plot(accuracy)
        plt.show()


def getCorrcoef(*lists):
    t = []
    for l in lists:
        t.append(l)
    return np.corrcoef(np.array(t))


def plotHist(data1, data2, title, xlabel, ylabel, legend1, legend2,
             cumulative=False):
    plt.figure()
    # list is ok but needs integer
    d1 = plt.hist(data1, hold=1, label=legend1, alpha=0.8,
                  cumulative=cumulative)
    d2 = plt.hist(data2, label=legend2, alpha=0.5, cumulative=cumulative)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc='center right')
    plt.grid(True)
    plt.savefig('hist ' + title)
    # plt.show(block=False)


def plotDatas(n, datas, title=None, xlabel=None, ylabel=None, legend=None):
    plt.figure()

    if title is not None:
        plt.title(title)

    if xlabel is not None:
        plt.xlabel(xlabel)

    if ylabel is not None:
        plt.ylabel(ylabel)

    for i in range(0, n):
        if legend is not None:
            plt.plot([j/10.0 for j in range(1, 10)], datas[i], label=legend[i])
    plt.legend(loc='center right')
    plt.ylim(0, 1)
    plt.savefig(title)
    plt.close()


def plot(n, x, y, title, xlabel, ylabel, grid=False):
    plt.figure()
    for i in range(0, n):
        plt.plot(x[i], y[i], '^')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.ylim(0, 30)
    plt.ylim(0, 1)
    # plt.grid(grid)
    # plt.savefig(title)
    # plt.legend(loc='center right')
    plt.show()


def getAccuracyList(report_path, raw_data_file_dir):
    """
    :param report_path: the full path of report_path
    :param raw_data_file_dir: the dir of raw data files
    :return: accuracy list ordered by raw data file name
    """
    files = os.listdir(raw_data_file_dir)
    results = {}
    accuracy = []
    # get result dicts
    with open(report_path) as f:
        lines = f.readlines()
        f.close()

        for line in lines:
            t = line.split('\t')
            file = t[0]
            d = eval(unicode(t[1]))
            if d:
                results[file] = d[u'result']

    for filename, result in results.items():
        # print result
        t = str(result).split('\n')
        t = t[0].split(',')
        sit_acc = float(t[0][13:])
        walk_acc = float(t[1][14:])
        if sit_acc > walk_acc:
            results[filename] = sit_acc
        else:
            results[filename] = walk_acc

    for file in files:
        if results.has_key(file):
            accuracy.append(results[file])

    accuracy = [float(accuracy[i]) for i in range(0, len(accuracy))]

    print '## totol test files in', raw_data_file_dir, len(files)
    print '## totol valid files in', raw_data_file_dir, len(results.items())

    return accuracy, len(files), len(results.items())


def plotBox(data1, data2, label1, label2, title, xlabel):
    plt.figure()
    plt.boxplot([data1, data2], vert=False, labels=[label1, label2])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.savefig('box ' + title)
    # plt.show(block=False)


def getQualified(data, threshold):
    i = 0
    for t in data:
        if t > threshold:
            i += 1
    rate = float(i) / len(data)
    return str(rate) + '(' + str(i) + '/' + str(len(data)) + ')'


def getDevided(x, y):
    return x / y


def getSortedCumulativeList(a1, a2):
    t = []
    for i in range(0, len(a1)):
        t.append([a1[i], a2[i], ])
    t.sort()

    r = []
    for i in range(0, len(t)):
        sum = 0
        for j in range(0, i + 1):
            sum += t[j][1]
        r.append([t[i][0], sum])

    return r


def getCumulativeList(l):
    r = []
    for i in range(0, len(l)):
        sum = 0
        for j in range(0, i + 1):
            sum += l[j]
        r.append(sum)

    return r


def getIncrementList(l):
    global sum
    r = []
    for i in range(0, len(l)):
        if i != 0:
            sum = l[i] - l[i - 1]
            r.append(sum)

    return r


def plotFFT(n, l, title, ret=False):
    plt.figure()
    for i in range(0, n):
        length = len(l[i])
        if 128 < length <= 256:
            # to 256 point
            for j in range(0, 256 - length):
                l[i].append(0)
        fft = np.fft.fft(l[i])
        a = [abs(fft[i]) for i in range(0, len(fft))]
        plt.plot(np.linspace(0, 2, len(fft)), a)
    # plt.ylim(0, 50)
    plt.xlim(0, 1)
    plt.title(title)
    plt.savefig(
        os.path.join('/home/cyrus/PycharmProjects/data_acc_r/fft/', title))
    plt.close('all')
    # plt.show(block=False)


def getFFT(l):
    length = len(l)
    N = np.ceil(np.log2(length))
    for i in range(0, int(np.power(2, N))-length):
        l.append(0)
    fft = np.fft.fft(l)
    a = [abs(fft[i]) for i in range(0, len(fft))]
    return a


def getHPF(n, datas, ftype='cheby2'):
    # iir filter parameter
    Wp = 0.1
    Ws = 0.01
    Rp = 1
    As = 3
    # filters ellip cheby2 cheby1 butter bessel
    b, a = fd.iirdesign(Wp, Ws, Rp, As, ftype=ftype)
    r = []
    for i in range(0, n):
        t = signal.filtfilt(b, a, datas[i])
        r.append(t.tolist())
        # fir filter parameter
        # f = 0.2 # cutoff = f * nyq
        # for i in range(0, n):
        #     b = signal.firwin(3, f, pass_zero=False, window='hamming')
        #     b = signal.firwin(7, f, pass_zero=False, window='blackman')
        #     b = signal.firwin(9, f, pass_zero=False, window='hann')
        # t = signal.filtfilt(b, [1], datas[i])
        # r.append(t.tolist())
    return r


def plotHist2d(x, y):
    """

    """
    plt.hist2d(x, y, bins=30)
    plt.show()


def plotKde(x, title, **kwargs):
    plt.figure()
    sns.set_palette('hls')
    plt.title(title)

    # this is a type of usage of **kwargs
    bins = kwargs.pop('bins', None)
    legend = kwargs.pop('legend', None)
    xlabel = kwargs.pop('xlabel', None)
    ylabel = kwargs.pop('ylabel', None)
    loc = kwargs.pop('loc', None)
    xlim = kwargs.pop('xlim', None)
    save = kwargs.pop('save', False)
    show = kwargs.pop('show', True)
    block = kwargs.pop('block', True)
    text = kwargs.pop('text', None)
    xlog = kwargs.pop('xlog', False)

    if legend is not None:
        sns.distplot(x, bins=bins, hist_kws={'label': legend},
                     kde_kws={'label': legend})
    else:
        sns.distplot(x, bins=bins)
        # plt.hist(x)
    if xlabel is not None:
        plt.xlabel(xlabel)
    if ylabel is not None:
        plt.ylabel(ylabel)
    if loc is not None:
        plt.legend(loc=loc)
    if xlim is not None:
        plt.xlim(xlim)
    if text is not None:
        ymin, ymax = plt.ylim()
        xmin, xmax = plt.xlim()
        plt.text(xmax * 0.01, ymax * 0.6, text)
    if xlog:
        plt.xscale('log')
    if save:
        plt.savefig(' '.join(['kde', title]))
    if show:
        plt.show(block=block)
    plt.close()
    return None


def plotSimpleKde(x, y=None, title=None, xlabel=None, ylabel=None, save=False):
    plt.figure()
    sns.set_palette('hls')
    sns.distplot(x, bins=100, hist_kws={'color': 'y', 'label': 'self'},
                 kde_kws={'color': 'y', 'label': 'self'})

    if y is not None:
        sns.distplot(y, hist_kws={'color': 'r', 'label': 'other'},
                     kde_kws={'color': 'r', 'label': 'other'})

    if title is not None:
        plt.title(title)

    if xlabel is not None:
        plt.xlabel(xlabel)

    if ylabel is not None:
        plt.ylabel(ylabel)

    # plt.xlim(0, 1)
    # plt.ylim(0, 8)

    if save:
        plt.savefig(title)

    plt.show()
    plt.close()


def plot3axisWave(title, x, y, z, fs):
    plt.figure()
    plt.subplot(311)
    plt.plot(x)
    # plt.xlim(0, fs)
    plt.subplot(312)
    # plt.xlim(0, fs)
    plt.plot(y)
    plt.subplot(313)
    # plt.xlim(0, fs)
    plt.plot(z)
    # plt.show()
    plt.savefig(title)
    plt.close()


def getHLRatio(x):
    # 128*0.6=76.8
    # 0~75, 76~127
    if len(x) != 256:
        print 'length error, length should be 256, current is', len(x)
        return []
    sum_all = 0.0
    sum_high = 0.0
    for i in range(0, 127):
        sum_all += x[i]
    for i in range(76, 127):
        sum_high += x[i]
    r = sum_high / sum_all
    # return r
    return 1 - r


def plotSimpleBox(x):
    plt.boxplot(x)
    plt.show()


def plotTimeFrequencyDomain(x):
    """special"""
    plt.figure()
    plt.subplot(211)
    plt.grid(True)
    plt.title('time domain')
    plt.ylabel('gyroscope(rad/s)')
    plt.xlabel('time')
    plt.plot(np.linspace(0, 3, 150), x)
    fft = getFFT(x)
    plt.subplot(212)
    plt.title('frequency domain(256-fft)')
    plt.ylabel('amplitude')
    plt.xlabel('omega(normalized)')
    plt.grid(True)
    plt.plot(np.linspace(0, 2, 256), fft)
    plt.show()


def getPercentile(x, percentile):
    return np.percentile(x, percentile)


def getNormalized(x):
    return pp.normalize(x)


def getDWT(x):
    pass


def plotSimplePlot(x,
                   y=None,
                   title=None,
                   xlegend=None,
                   ylegend=None,
                   xlabel=None,
                   ylabel=None):
    plt.plot(x, 'r*', label=xlegend)
    if title is not None:
        plt.title(title)
    if xlabel is not None:
        plt.xlabel(xlabel)
    if ylabel is not None:
        plt.ylabel(ylabel)
    if y is not None:
        plt.plot(y, 'bo', label=ylegend)
    plt.legend(loc='center right')
    plt.show()


def getSorted(l):
    length = len(l)
    r = []
    for i in range(0, length):
        min_ = min(l)
        r.append(min_)
        l.remove(min_)
    return r


def plotSimpleXY(x, y, title,
                 x1=None, y1=None, xlabel=None, ylabel=None,
                 legend1=None, legend2=None,
                 show=True, save=False):
    plt.title(title)
    plt.plot(x, y, 'o', label=legend1)
    if x1 is not None and y1 is not None:
        plt.plot(x1, y1, '^', label=legend2)
    if xlabel is not None and ylabel is not None:
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
    plt.legend(loc='upper center')
    if save:
        plt.savefig(title)
    if show:
        plt.show()


def getAccuracyFromPredictionFile(prediction_file, threshold,
                                  new=False, all=False):
    """
    You can get accuracy from the original prediction file.

    A prediction file is generated by svm-prediction or vw. It looks
    like below:
        labels 1 0
        1 0.975596 0.024404 1
        1 0.859735 0.140265 1
        omit..
        Accuracy = 98.0636% (709/723) (classification)
    The accuracy which shows at the last line is calculated by the
    svm-prediction or vw, it is determined by the threshold you set in the svm
    -prediction or vw. You can set different threshold, so that you can
    gain different result. If the prediction file changes, you have to modified
    the code below correspondingly.

    The way we calculate the normal accuracy is:
        let the count of prediction which larger that threshold be m
        let the count of prediction which lower that threshold be n
        then
            accuracy = m / (m+n)

    :param all: whether get original accuracy
    :param new: whether use new algorithm or not
    :param threshold: threshold to determined which is positive(larger that t).
    :param prediction_file: full path of a prediction file
    :type all: bool
    :type new: bool
    :type threshold: float
    :type prediction_file: basestring
    :return accuracy: the accuracy responding to the threshold
    """

    global new_accuracy
    m = 0  # number of prediction > threshold
    n = 0  # number of prediction < threshold

    with open(prediction_file) as f:
        lines = f.readlines()
        f.close()
        # remove head and tail
        lines.remove(lines[0])
        lines.pop()

        # get m, n
        for line in lines:
            t = line.split(' ')
            prediction = float(t[1])
            if prediction >= threshold:
                m += 1
            else:
                n += 1

    # if there is solution
    solution = False
    # check m and n
    if m == 0 and n == 0:
        raise ValueError('There is no valid data in prediction file')
    elif not new:
        old_accuracy = float(m) / (m + n)  # calculate normal accuracy
    else:
        old_accuracy = float(m) / (m + n)  # calculate normal accuracy
        # new algorithm
        if m == 1 or n == 1 or m == 0 or n == 0:
            new_accuracy = old_accuracy
            solution = True

        elif m >= n:
            for i in range(0, n):
                for j in range(0, m):
                    if 2 * i > n or i + j < n or 2 * j >= m:
                        continue
                    else:
                        if i == 0:
                            continue
                        new_accuracy = (m - j) / float(m - j + i)
                        solution = True
                        break
                if solution:
                    break
        else:
            for i in range(n, 0, -1):
                for j in range(m, 0, -1):
                    if 2 * i <= n or i + j > n or 2 * j < m:
                        continue
                    else:
                        new_accuracy = (m - j) / float(m - j + i)
                        solution = True
                        break
                if solution:
                    break

    if not new:
        return old_accuracy
    else:
        if not solution:
            if all is not None:
                return old_accuracy, old_accuracy
            else:
                return old_accuracy
        else:
            if all is not None:
                return old_accuracy, new_accuracy
            else:
                return new_accuracy


def plotHeat(x, title):
    cmap = sns.cubehelix_palette(n_colors=30, start=3, rot=5, dark=0.6,
                                 reverse=True,
                                 gamma=2, as_cmap=True)
    mask = None
    # mask = np.ones_like(x)
    # mask[getCrossZeroIndices(x)] = False
    if type(x) is list:
        x = np.array(x)
        x = x.T
    sns.heatmap(x, linewidths=0.05, cmap=cmap, center=0, annot=True, mask=mask)
    plt.yticks([float(i) + 0.5 for i in range(0, 11)],
               [str(i/10.0) for i in range(0, 11)],
               rotation=0)
    plt.xticks([float(i) + 0.5 for i in range(0, 11)],
               [str(i/10.0) for i in range(0, 11)],
               rotation=0)
    plt.xlabel('threshold')
    plt.ylabel('acceptance')
    plt.title(title)
    plt.show()
    # plt.savefig(title)


def getCrossZeroIndices(table):
    """
    :type table: list
    """
    array_row = []
    array_col = []

    before = 1
    after = 1
    for row in table:
        for item in row:
            if item*before > 0:
                after *= 1
            else:
                after *= -1
            if 0 > after * before:
                array_row.append(table.index(row))
                array_col.append(row.index(item))
            before = after
    return np.array(array_row), np.array(array_col)




