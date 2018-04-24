from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import os
import random
import sys

import tensorflow as tf

# how many to be train set
_NUM_TRAIN = 1
# how many class you want
_CLASS_UPPER_LIMIT = 1000
# how many window files you want
_FILE_LOWER_LIMIT = 14000
# how many files in one tfrecord file
_NUM_PER_SHARD = 40000

_LABELS_FILENAME = 'labels.txt'
_RANDOM_SEED = 0


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


def _write_label_file(labels_to_class_names, dataset_dir, filename=_LABELS_FILENAME):
    """Writes a file with the list of class names.

    Args:
      labels_to_class_names: A map of (integer) labels to class names.
      dataset_dir: The directory in which the labels file should be written.
      filename: The filename where the class names are written.
    """
    labels_filename = os.path.join(dataset_dir, filename)
    with open(labels_filename, 'w') as f:
        for label in labels_to_class_names:
            class_name = labels_to_class_names[label]
            f.write('%d:%s\n' % (label, class_name))


@profile
def _get_filenames_and_classes(root):
    class_names = []

    # for classname in os.listdir(root):


    # path = root/classname/
    for classname in os.listdir(root):
        path = os.path.join(root, classname)
        if os.path.isdir(path) and len(os.listdir(path)) >= _FILE_LOWER_LIMIT:
            class_names.append(classname)

    random.seed(_RANDOM_SEED)
    random.shuffle(class_names)
    class_names = class_names[:_CLASS_UPPER_LIMIT]

    window_filenames = []
    for classname in class_names:
        directory = os.path.join(root, classname)

        filenames = os.listdir(os.path.join(root, classname))
        random.seed(_RANDOM_SEED)
        random.shuffle(filenames)
        filenames = filenames[:_FILE_LOWER_LIMIT]

        for filename in filenames:
            path = os.path.join(directory, filename)
            window_filenames.append(path)

    return window_filenames, sorted(class_names)


def _get_dataset_filename(dataset_dir, split_name, shard_id):
    output_filename = 'riskcog_%s_%05d.tfrecord' % (
        split_name, shard_id)
    return os.path.join(dataset_dir, output_filename)


@profile
def _convert_dataset_to_tfrecord(split_name, filenames, class_names_to_ids, dataset_dir):
    """Converts the given filenames to a TFRecord dataset.

    Args:
      split_name: The name of the dataset, either 'train' or 'validation'.
      filenames: A list of absolute paths to png or jpg images.
      class_names_to_ids: A dictionary from class names (strings) to ids
        (integers).
      dataset_dir: The directory where the converted datasets are stored.
    """
    assert split_name in ['train', 'validation']

    NUM_SHARDS = int(math.ceil(len(filenames) / float(_NUM_PER_SHARD)))

    for shard_id in range(NUM_SHARDS):
        # filename: riskcog_train_shard_id.tfrecord
        output_filename = _get_dataset_filename(dataset_dir, split_name, shard_id)

        with tf.python_io.TFRecordWriter(output_filename) as tfrecord_writer:
            start_ndx = shard_id * _NUM_PER_SHARD
            end_ndx = min((shard_id + 1) * _NUM_PER_SHARD, len(filenames))

            for i in range(start_ndx, end_ndx):
                sys.stdout.write('\r>> Converting window %d/%d shard %d for %s' % (
                    i + 1, len(filenames), shard_id, split_name))
                sys.stdout.flush()

                # Read the filename:
                # image_data = tf.gfile.FastGFile(filenames[i], 'rb').read()
                with open(filenames[i]) as f:
                    # window_data = tf.gfile.FastGFile(filenames[i], 'rb').read()
                    window_data = [float(line) for line in f]

                class_name = os.path.basename(os.path.dirname(filenames[i]))
                class_id = class_names_to_ids[class_name]

                example = tf.train.Example(features=tf.train.Features(
                    feature={
                        'window/encoded': _float_feature(window_data),
                        'window/label': _int64_feature(class_id),
                    }))
                tfrecord_writer.write(example.SerializeToString())

    sys.stdout.write('\n')
    sys.stdout.flush()

def get_size(filenames):
    size = 0
    for filename in filenames:
        size += os.path.getsize(filename)

    return round(size/1024/1024, 3)


@profile
def main():
    # root = sys.argv[-2]
    # target = sys.argv[-1]
    root = '/home/linzi/txdata/largeScale_Test_TX_LSTM/balanceDataSet/txData_Window_75'
    target = 'tfrecord-for-1000-40000'

    if not os.path.exists(target):
        os.mkdir(target)

    window_filenames, class_names = _get_filenames_and_classes(root)
    print('>> number of window files', len(window_filenames))
    print('>> number of classes', len(class_names))
    # print('>> size of window files', get_size(window_filenames))

    class_names_to_ids = dict(zip(class_names, range(len(class_names))))

    # Divide into train and test:
    random.seed(_RANDOM_SEED)
    random.shuffle(window_filenames)
    training_filenames = window_filenames[:int(_NUM_TRAIN * len(window_filenames))]
    validation_filenames = window_filenames[int(_NUM_TRAIN * len(window_filenames)):]

    # First, convert the training and validation sets.
    _convert_dataset_to_tfrecord('train', training_filenames, class_names_to_ids, target)
    _convert_dataset_to_tfrecord('validation', validation_filenames, class_names_to_ids, target)

    # Finally, write the labels file:
    labels_to_class_names = dict(zip(range(len(class_names)), class_names))
    _write_label_file(labels_to_class_names, target)

    print('\nFinished converting the riskcog dataset!')


if __name__ == '__main__':
    main()
