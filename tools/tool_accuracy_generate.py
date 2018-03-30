"""
crosscheck accuracy generate by prediction file

INPUT:
prediction file, threshold

OUTPUT:
accuracy results which are like below:
    861157030061416:861157030061416:98.3402% (711/723)
    861157030061416:861157030061hpf:44.3983% (321/723)
    ...
    861157030061416:869798020042hpf:4.97925% (36/723)
    861157030061416:A1000049CD8169:7.19225% (52/723)

HOW TO USE:
configure the full path of prediction file
configure the threshold
"""

import os

import tools

# -----------------------------------------------------------------------
root = '/home/cyrus/Desktop/MyInternshipProject/WeekSummary/6/' \
       'new accuracy algorithm'
# prediction_dir = ['5_people', 'ant', 'tx_130']
# prediction_dir = ['5_people', 'ant']
# prediction_dir = ['5_people', 'tx_130']
prediction_dir = ['5_people']
# prediction_dir = ['ant']
# prediction_dir = ['tx_130']
threshold = 0.35
# -----------------------------------------------------------------------
result_file = '../result_gen_{0}%_{1}'.format(str(int(threshold * 100)),
                                              prediction_dir[0])
# -----------------------------------------------------------------------


if os.path.exists(result_file):
    os.remove(result_file)

# get accuracy and write them into result file
for dir in prediction_dir:
    files = os.listdir(os.path.join(root, dir))
    for file in files:
        # print '# current file is', file
        full_path = os.path.join(root, dir, file)

        # test_imei1:train_imei2.output
        t = file.split(':')
        test = t[0].split('_')[1]
        train = t[1].split('_')[1].split('.')[0]
        test_new = "{0}{1}%".format(test[:-3], str(int(threshold * 100)))
        train_new = "{0}{1}%".format(train[:-3], str(int(threshold * 100)))

        if train == test:
            try:
                new = tools.getAccuracyFromPredictionFile(full_path, threshold)
                old = tools.getAccuracyFromPredictionFile(full_path, 0.5)
            except ValueError:
                continue
        else:
            try:
                new = tools.getAccuracyFromPredictionFile(full_path, threshold)
                old = tools.getAccuracyFromPredictionFile(full_path, 0.5)
            except ValueError:
                continue

        # write
        with open(result_file, 'a') as f:
            f.write(':'.join([test, train, '{0}%\n'.format(old * 100)]))
            f.write(':'.join([test_new, train_new, '{0}%\n'.format(new * 100)]))
            f.flush()
            f.close()
# sort
lines = []
with open(result_file) as f:
    lines = f.readlines()
    lines.sort()
    f.close()

with open(result_file, 'w') as f:
    f.writelines(lines)
    f.flush()
    f.close()

print 'result file save at', result_file
