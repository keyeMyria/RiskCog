"""
This is a realization on "Human activity recognition using
wearable sensors by deep convolution neural networks."

This is version 1

Author: Qiang(liuqiangqhtf@163.com)
"""
import os

import numpy as np
import tensorflow as tf


def input_pipeline(root, usage, batch_size=10, window_size=75, class_size=3):
    def _parse_function(example_proto):
        features = {'window/encoded': tf.VarLenFeature(tf.float32),
                    'window/label': tf.FixedLenFeature((), tf.int64, default_value=0)}
        parsed_features = tf.parse_single_example(example_proto, features)
        window = tf.reshape(tf.sparse_tensor_to_dense(parsed_features['window/encoded']),
                            shape=(window_size, 32, 68, 1))

        label = tf.one_hot(parsed_features['window/label'], class_size)
        return window, label

    filenames = [os.path.join(root, usage, filename) for filename in os.listdir(os.path.join(root, usage))]

    dataset = tf.data.TFRecordDataset(filenames)
    dataset = dataset.map(_parse_function)
    dataset = dataset.batch(batch_size)
    iterator = dataset.make_initializable_iterator()

    return iterator, iterator.get_next()


def CNN_ONLY():
    X = tf.placeholder(tf.float32, [None, 36, 68, 1])
    # 1st
    # ==> bs*36*68*1
    # conv, in_channel=1, out_channels=5, kernel_size=(5, 5), strides=(1, 1), valid
    W_1 = tf.Variable(tf.truncated_normal([5, 5, 1, 5]), name='w_conv_1')
    B_1 = tf.Variable(tf.constant(0.1, shape=[32]), name='b_conv_1')
    CONV_1 = tf.nn.relu(tf.nn.conv2d(X, W_1, strides=[1, 1, 1, 1], padding='VALID') + B_1)
    # ==> 32*64*5
    # avg_p, ksize=(4, 4), strides=(1, 1)
    POOL_1 = tf.nn.max_pool(CONV_1, ksize=[1, 4, 4, 1], strides=[1, 1, 1, 1], padding='SAME')
    # ==> 8*16*5
    # 2nd
    # ==> 8*16*5
    # conv, in_channel=5, out_channels=10, kernel_size=(5, 5), strides=(1, 1), valid
    W_2 = tf.Variable(tf.truncated_normal([5, 5, 5, 10]), name='w_conv_2')
    B_2 = tf.Variable(tf.constant(0.1, shape=[10]), name='b_conv_2')
    CONV_2 = tf.nn.relu(tf.nn.conv2d(POOL_1, W_2, strides=[1, 1, 1, 1], padding='VALID') + B_2)
    # ==> 4*12*10
    # avg_p, ksize=(2, 2), strides=(1, 1)
    POOL_2 = tf.nn.avg_pool(CONV_2, ksize=[1, 2, 2, 1], strides=[1, 1, 1, 1], padding='SAME')
    # ==> 2*6*10
    # 3rd
    # dense, 120
    W_3 = tf.Variable(tf.truncated_normal([2 * 6 * 10, 120]), name='w_dense_1')
    B_3 = tf.Variable(tf.constant(0.1, shape=[120]), name='b_dense_1')
    POOL_2_FLAT = tf.reshape(POOL_2, [-1, 2 * 6 * 10])
    DENSE_3 = tf.nn.relu(tf.matmul(POOL_2_FLAT, W_3) + B_3)
    # KP = tf.placeholder(tf.float32)
    # DENSE_3 = tf.nn.dropout(DENSE_3, KP)
    # output
    # softmax, 6
    W_4 = tf.Variable(tf.truncated_normal([120, 6]), name='w_softmax')
    B_4 = tf.Variable(tf.constant(0.1, shape=[6]), name='b_softmax')
    return tf.nn.softmax(tf.matmul(DENSE_3, W_4) + B_4)


def main():
    DATA_PATH = ''
    batch_size = 120
    class_size = 6
    training_epochs = 100

    # optimizer
    Y_ONLY_CNN = CNN_ONLY()  # network
    Y = tf.placeholder(tf.float32, [None, 6])  # label
    cross_entropy = tf.reduce_mean(-tf.reduce_sum(Y * tf.log(Y_ONLY_CNN), reduction_indices=[1]))
    cost = cross_entropy
    optimizer = tf.train.GradientDescentOptimizer(0.01).minimize(cost)

    # predictor
    correct_prediction = tf.equal(tf.argmax(Y_ONLY_CNN, 1), tf.argmax(Y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    # input
    X = tf.placeholder(tf.float32, [None, 32, 68, 1])
    train_iterator, train_batch = input_pipeline(
        root=DATA_PATH, usage='train', batch_size=batch_size, class_size=class_size)
    test_iterator, test_batch = input_pipeline(
        root=DATA_PATH, usage='test', batch_size=batch_size, class_size=class_size)

    # run
    with tf.Session() as sess:
        sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])

        for i in range(0, training_epochs):
            message = []
            sess.run(train_iterator.initializer)
            while True:
                try:
                    window_batch, label_batch = sess.run(train_batch)
                    _, _cost, _accuracy = sess.run(
                        [optimizer, cost, accuracy], feed_dict={X: window_batch, Y: label_batch})
                    message.append([_cost, _accuracy])

                except tf.errors.OutOfRangeError:
                    break
            print(np.mean(message, axis=0))

            message = []
            sess.run(test_iterator.initializer)
            while True:
                try:
                    window_batch, label_batch = sess.run(test_batch)
                    _, _cost, _accuracy = sess.run(
                        [Y_ONLY_CNN, cost, accuracy], feed_dict={X: window_batch, Y: label_batch})
                    message.append([_cost, _accuracy])
                except tf.errors.OutOfRangeError:
                    break
            print(np.mean(message, axis=0))
            print('>> train iter {0} done'.format(i + 1))


if __name__ == '__main__':
    main()
