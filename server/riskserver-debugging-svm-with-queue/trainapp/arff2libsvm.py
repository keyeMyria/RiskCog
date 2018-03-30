# Description : Data processing script for LaSVM.
# Project     : Mobile Risk Management (EECS 495 - Winter 2016, Northwestern University)
# Author      : Sandeep Raju Prabhakar <SandeepPrabhakar2015@u.northwestern.edu>

import argparse
import os


def dim_redu(x, j, mode):
    buff = []
    x = x.split(' ')
    for i in range(len(x)):
        if i != 0:
            x[i] = x[i].split(':')[1]
            x[i] = x[i].split(' ')[0]
            buff.append(x[i])
    order = 0
    lent = 0
    buf = ''
    for i in range(len(buff)):
        if i != (len(buff) - 1):
            if i == 0:
                buf = mode + ' '
            if -1 not in j:
                for k in j:
                    if i == k * 3 or i == k * 3 + 1 or i == k * 3 + 2 or i == 30 or i == k * 3 + 31 or i == k * 3 + 32 or i == k * 3 + 33 or i == 61:
                        order = order + 1
                        buf += (str(order - 1) + ':' + buff[i] + ' ')
                        break
            else:
                order = order + 1
                buf += (str(order - 1) + ':' + buff[i] + ' ')
        else:
            if -1 not in j:
                for k in j:
                    if i == k * 3 or i == k * 3 + 1 or i == k * 3 + 2 or i == 30 or i == k * 3 + 31 or i == k * 3 + 32 or i == k * 3 + 33 or i == 61:
                        order = order + 1
                        buf += (str(order - 1) + ':' + buff[i])
                        break
            else:
                order = order + 1
                buf += (str(order - 1) + ':' + buff[i])
    return buf


def arff2svmlight(source, destination):
    print '## TRACE ##', 'converting arff to svmlight', source, destination
    """`arff2svmlight` converts a data file in arff format
    to the libsvm's svmlight format.
    Format details are here: http://leon.bottou.org/projects/lasvm (Implementation section)

    The gist:
    <line>    = <target> <feature>:<value> ... <feature>:<value>
    <target>  = +1 | -1  <int>
    <feature> = <integer>
    <value>   = <float>
    """
    # TODO: fix the way of specifying the label
    # TARGET_FLAG = 1  can be either +1 or -1
    with open(source, 'r') as sf:
        with open(destination, 'w') as df:
            for line in sf.readlines():
                # process each line from the arff file
                if "nan" in line.lower() or line.strip() == '':
                    # skip the nan line
                    continue
                line = line.strip()
                features = line.split()
                # TODO: check this -- some features to ignore
                postural_data = features[-1]  # TODO: should this be included?
                imei_number = features[-2]  # TODO: should this be ignored?

                # convert each feature to the appropriate format in svmlight format.
                format = '%s %s\n'
                arff = imei_number + ' ' + ' '.join([
                    ':'.join(i) for i in zip([
                        str(num) for num in range(len(features))
                    ], features[:-2])  # TODO: ignoring last 2 features. get this clarified.
                ])
                buf = dim_redu(arff, [0, 7, 8, 9], features[-2])
                df.write('%s\n' % (buf))


def arff2vowpalwabbit(source, destination):
    """`arff2vowpalwabbit` converts data file in arff format
    to the vowpal wabbit's compatible format.
    Format details are here: https://github.com/JohnLangford/vowpal_wabbit/wiki/Input-format

    Though the format is extensive, a very simple implementation is done below.

    The gist:
    <line>    = <target> | <feature>:<value> ... <feature>:<value>
    <target>  = +1 | -1  <int>
    <feature> = <integer>
    <value>   = <float>
    
    Perl oneliner to convert libsvm (svmlight) format to vowpal wabbit format:
    perl -pe 's/\s/ | /' data.libsvm | vw -f model
    """
    # TODO: fix the way of specifying the label
    TARGET_FLAG = 1  # can be either +1 or -1

    with open(source, 'r') as sf:
        with open(destination, 'a') as df:
            for line in sf:
                # process each line from the arff file
                features = line.split()

                # TODO: check this -- some features to ignore
                postural_data = features[-1]  # TODO: should this be included?
                imei_number = features[-2]  # TODO: should this be ignored?

                # convert each feature to the appropriate format in svmlight format.
                format = '%s | %s\n'
                df.write(format % (TARGET_FLAG, ' '.join([
                    ':'.join(i) for i in zip([
                        str(num) for num in range(len(features))
                    ], features[:-2])  # TODO: ignoring last 2 features. get this clarified.
                ])))


def main():
    # define an argument parser and configure it's arguments
    parser = argparse.ArgumentParser(
        description='Parses the arff data to svmlight format.')
    parser.add_argument('source', help=('Path to the data source. Either a directory or a file path'))
    parser.add_argument('destination', help=('Path to the data destination. Either a directory or a file path'))

    args = parser.parse_args()

    # normalize the source and destination paths
    source_path = os.path.abspath(args.source)
    destination_path = os.path.abspath(args.destination)

    # check the validity of the source and destination
    if os.path.exists(destination_path):
        # there is already a file or a directory at the
        # path specified as the destination.
        print '[error] invalid destination. destination already exists.'
        return

    # check if the source is a directory or a file
    if os.path.isdir(source_path):
        # create the destination directory
        print '[creating-directory]', destination_path
        os.mkdir(destination_path)

        # walk the hierarchy of the source directory.
        for root, dirs, files in os.walk(source_path):
            # get the relative path from the root
            relative_path = root.split(source_path)[1].lstrip('/')

            # create all the directories.
            for d in dirs:
                os.mkdir(os.path.join(destination_path, relative_path, d))

            # process all the files.
            for f in files:
                abs_file_path = os.path.join(root, f)
                print' [processing]', abs_file_path
                arff2svmlight(abs_file_path, os.path.join(destination_path, relative_path, f))

    elif os.path.isfile(source_path):
        print' [processing]', source_path
        arff2svmlight(source_path, destination_path)

    else:
        print '[error] invalid source path. source is neither a file nor a directory.'


if __name__ == '__main__':
    main()
#
# arff2svmlight('/home/cyrus/Public/riskserver-final/vw_test/mary/20170731041240.arff', '/home/cyrus/Public/riskserver-final/vw_test/mary/####.libsvm')
