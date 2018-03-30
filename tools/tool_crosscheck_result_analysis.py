"""
crosscheck result analysis

INPUT:
When we use semi-director approach, we can use this to analyze that accuracy
results.

The result is like below:
    861157030061416:861157030061416:98.3402% (711/723)
    861157030061416:861157030061hpf:44.3983% (321/723)
    ...
    861157030061416:869798020042hpf:4.97925% (36/723)
    861157030061416:A1000049CD8169:7.19225% (52/723)

OUTPUT:
We can generate the result table of mean of accuracy for owner and others,
which is like below:
    +---------+---------------+----------------+
    |         |     others    |      self      |
    +---------+---------------+----------------+
    |   raw   |  13.261247664 | 93.1006147059  |
    |   new   | 15.4242443235 | 93.2491352941  |
    |  differ | 2.16299665954 | 0.148520588235 |
    +---------+---------------+----------------+

HOW TO USE:
configure the ROOT dir which contains the accuracy results
configure the RESULT_DIR where you want to save the result table
configure the KEY if you preprocess the raw data, if not, you can skip it
configure the FORMAT to control the format of results
configure the file of accuracy results
"""

import os

from prettytable import PrettyTable

import tools

# --------------------------------------------------------
# configuration
ROOT = '..'
RESULT_DIR = '..'
FORMAT = '%.8f'
# --------------------------------------------------------
KEY = 'new'
file = 'result_f.txt'
result_file = 'ant4'
# --------------------------------------------------------

# auto get imeis_raw and imeis_new
imeis = []
imeis_raw = []
imeis_new = []
# get all
filepath = os.path.join(ROOT, file)

with open(filepath) as f:
    lines = f.readlines()
    lines.sort()
    f.close()

with open(filepath, 'w') as f:
    f.writelines(lines)
    f.flush()
    f.close()

with open(filepath) as f:
    lines = f.readlines()
    f.close()
    for line in lines:
        t = line.split(':')
        imeis.append(t[0])
# separate and filter
for imei in imeis:
    if imei.endswith(KEY):
        if imei not in imeis_new:
            imeis_new.append(imei)
        else:
            pass
    else:
        if imei not in imeis_raw:
            imeis_raw.append(imei)
        else:
            pass

# auto generate prettytable column name
result_table = PrettyTable(['', 'others', 'self'])

accuracy_raw_set = []
accuracy_new_set = []
l = len(imeis_raw)
index = 0
# try to get accuracy set with raw files
# try to get accuracy set with handled files
for imeis in (imeis_raw, imeis_new):
    for i in range(0, len(imeis)):
        self = imeis[i]
        tmp = []
        with open(filepath, 'r') as f:
            lines = f.readlines()
            f.close()
            for line in lines:
                t = line.split(':')
                if t[1] == self and index == 0 and not t[0].endswith(KEY):
                    pass
                elif t[1] == self and index == 1 and t[0].endswith(KEY):
                    pass
                else:
                    continue
                t[2] = FORMAT % float(t[2].split('%')[0])
                tmp.append(float(t[2]))
            if index == 0:
                accuracy_raw_set.append(tmp)
            else:
                accuracy_new_set.append(tmp)
    index += 1

# try to get the difference between raw and new
different_set = []
for i in range(0, len(imeis_raw)):
    tmp = []
    for j in range(0, len(imeis_raw)):
        a = FORMAT % (
        float(accuracy_new_set[i][j]) - float(accuracy_raw_set[i][j]))
        tmp.append(float(a))
    different_set.append(tmp)

# calculate the means
index = 0
for accuracy_set in (accuracy_raw_set, accuracy_new_set, different_set):
    mean_t = []
    tmp3 = []
    mean_p = []
    for i in range(0, l):
        tmp1 = []
        tmp2 = []
        for j in range(0, l):
            if i == j:
                # be tested by itself
                tmp3.append(accuracy_set[i][j])
            else:
                tmp1.append(accuracy_set[i][j])
                tmp2.append(accuracy_set[j][i])
        mean_t.append(tools.getMean(tmp1))
        mean_p.append(tools.getMean(tmp2))
    mean_1 = tools.getMean(mean_t)
    mean_2 = tools.getMean(mean_p)
    mean_3 = tools.getMean(tmp3)
    if index == 0:
        label = 'raw'
    elif index == 1:
        label = 'new'
    else:
        label = 'different'
    index += 1
    # result_table.add_row([label, mean_1, mean_2, mean_3])
    result_table.add_row([label, mean_1, mean_3])

result_path = os.path.join(RESULT_DIR, result_file)
print '# result save at', result_path
with open(result_path, 'w') as f:
    f.write(result_table.get_string())
    f.write('\nnegative figure will be better for others\n')
    f.write('positive figure will be better for himself\n')
    f.close()
