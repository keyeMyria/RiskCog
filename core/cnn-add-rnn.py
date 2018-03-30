"""
This is a realization on "Deep convolutional and
lstm recurrent neural networks for multimodal wearable
activity recognition"

This is version 1

Author: Qiang(liuqiangqhtf@163.com)
"""
import os

import numpy as np
import tensorflow as tf


def input_pipeline(root, usage, batch_size=10, window_size=75, class_size=3, feature_size=9):
    def _parse_function(example_proto):
        features = {'window/encoded': tf.VarLenFeature(tf.float32),
                    'window/label': tf.FixedLenFeature((), tf.int64, default_value=0)}
        parsed_features = tf.parse_single_example(example_proto, features)
        window = tf.reshape(tf.sparse_tensor_to_dense(parsed_features['window/encoded']),
                            shape=(75, feature_size, 1))

        label = tf.one_hot(parsed_features['window/label'], class_size)
        return window, label

    filenames = [os.path.join(root, usage, filename) for filename in os.listdir(os.path.join(root, usage))]

    dataset = tf.data.TFRecordDataset(filenames)
    dataset = dataset.map(_parse_function)
    dataset = dataset.batch(batch_size)
    iterator = dataset.make_initializable_iterator()

    return iterator, iterator.get_next()


def print_activations(t):
    print(t.op.name, ' ', t.get_shape().as_list())


def cnn_add_rnn(X, batch_size, class_size, feature_size):
    # 1st
    # ==> bs*75*9*1
    # conv, in_channel=1, out_channels=64, kernel_size=(5, 1), strides=(1, 1), valid
    w_1 = tf.Variable(tf.truncated_normal([5, 1, 1, 64], stddev=0.1), name='w_conv_1')
    b_1 = tf.Variable(tf.constant(0.002, shape=[64]), name='b_conv_1')
    conv_1 = tf.nn.relu(tf.nn.conv2d(X, w_1, strides=[1, 1, 1, 1], padding='VALID') + b_1, name='conv_1')
    # print_activations(conv_1)
    # ==> 71*9*64
    # 2nd
    # ==> 71*9*64
    # conv, in_channel=64, out_channels=64, kernel_size=(5, 1), strides=(1, 1), valid
    w_2 = tf.Variable(tf.truncated_normal([5, 1, 64, 64], stddev=0.1), name='w_conv_2')
    b_2 = tf.Variable(tf.constant(0.002, shape=[64]), name='b_conv_2')
    conv_2 = tf.nn.relu(tf.nn.conv2d(conv_1, w_2, strides=[1, 1, 1, 1], padding='VALID') + b_2, name='conv_2')
    # print_activations(conv_2)
    # ==> 67*9*64
    # 3rd
    # ==> 67*9*64
    # conv, in_channel=64, out_channels=64, kernel_size=(5, 1), strides=(1, 1), valid
    w_3 = tf.Variable(tf.truncated_normal([5, 1, 64, 64], stddev=0.1), name='w_conv_3')
    b_3 = tf.Variable(tf.constant(0.002, shape=[64], name='b_conv_3'))
    conv_3 = tf.nn.relu(tf.nn.conv2d(conv_2, w_3, strides=[1, 1, 1, 1], padding='VALID') + b_3, name='conv_3')
    # print_activations(conv_3)
    # ==> 63*9*64
    # 4th
    # ==> 63*9*64
    # conv, in_channel=64, out_channels=64, kernel_size=(5, 1), strides=(1, 1), valid
    w_4 = tf.Variable(tf.truncated_normal([5, 1, 64, 64], stddev=0.1), name='w_conv_4')
    b_4 = tf.Variable(tf.constant(0.002, shape=[64], name='b_conv_4'))
    conv_4 = tf.nn.relu(tf.nn.conv2d(conv_3, w_4, strides=[1, 1, 1, 1], padding='VALID') + b_4, name='conv_4')
    # print_activations(conv_4)
    # ==> 59*9*64
    # 5th
    # reshape, bs*59*9*64 => bs*59*(9*64)
    conv_4_reshape = tf.reshape(tf.transpose(conv_4, [0, 1, 3, 2]), [-1, 59, feature_size*64], name='conv_4_reshape')
    # lstm*2, bs*time_steps*input_size, time_steps=59, input_size=64*9, units=128
    lstm_1 = tf.contrib.rnn.BasicLSTMCell(num_units=128, forget_bias=1.0, state_is_tuple=True)
    lstm_1_dropout = tf.nn.rnn_cell.DropoutWrapper(lstm_1, output_keep_prob=0.5)
    lstm_2 = tf.contrib.rnn.BasicLSTMCell(num_units=128, forget_bias=1.0, state_is_tuple=True)
    lstm_2_dropout = tf.nn.rnn_cell.DropoutWrapper(lstm_2, output_keep_prob=0.5)
    lstm_cells = tf.contrib.rnn.MultiRNNCell([lstm_1_dropout, lstm_2_dropout], state_is_tuple=True)
    outputs, states = tf.nn.dynamic_rnn(lstm_cells, conv_4_reshape, dtype=tf.float32)
    print_activations(outputs)
    output = tf.transpose(outputs, [1, 0, 2])[-1]
    print_activations(output)
    # ==> bs*128
    # 7th
    # softmax, class_size
    w_7 = tf.Variable(tf.truncated_normal([128, class_size], stddev=0.1), name='w_softmax')
    b_7 = tf.Variable(tf.constant(0.002, shape=[class_size], name='b_softmax'))
    softmax = tf.nn.softmax(tf.matmul(output, w_7) + b_7)
    print_activations(softmax)

    return softmax


def main():
    DATA_PATH = '../dataset/tuning-10-1000'
    batch_size = 500
    class_size = 10
    training_epochs = 100
    feature_size = 9


    # network
    X = tf.placeholder(tf.float32, [None, 75, feature_size, 1])
    KP = tf.placeholder(tf.float32)
    Y_CNN_ADD_RNN = cnn_add_rnn(X, batch_size, class_size, feature_size)  # network

    # optimizer
    Y = tf.placeholder(tf.float32, [None, class_size])  # label
    l2 = 0.0 * sum(tf.nn.l2_loss(tf_var) for tf_var in tf.trainable_variables())
    cost = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(labels=Y, logits=Y_CNN_ADD_RNN)
    ) + l2

    global_step = tf.Variable(0)
    learning_rate = tf.train.exponential_decay(1e-3, global_step, decay_steps=8, decay_rate=0.9, staircase=True)
    # optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost, global_step=global_step)
    optimizer = tf.train.AdamOptimizer(learning_rate).minimize(cost, global_step=global_step)
    # optimizer = tf.train.AdamOptimizer(0.0001).minimize(cost)

    # predictor
    correct_prediction = tf.equal(tf.argmax(Y_CNN_ADD_RNN, 1), tf.argmax(Y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, dtype=tf.float32))

    # input
    train_iterator, train_batch = input_pipeline(
        root=DATA_PATH, usage='train', batch_size=batch_size, class_size=class_size, feature_size=feature_size)
    test_iterator, test_batch = input_pipeline(
        root=DATA_PATH, usage='test', batch_size=batch_size, class_size=class_size, feature_size=feature_size)

    # run
    with tf.Session() as sess:
        sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])
        # print(np.sum([np.prod(v.get_shape().as_list()) for v in tf.trainable_variables()]))

        for i in range(0, training_epochs):
            message = []
            sess.run(train_iterator.initializer)

            # print(sess.run(global_step))

            while True:
                try:
                    window_batch, label_batch = sess.run(train_batch)
                    if window_batch.shape[0] == batch_size:
                        _, _cost, _accuracy = sess.run(
                            [optimizer, cost, accuracy], feed_dict={X: window_batch, Y: label_batch, KP: 0.5})
                        message.append([_cost, _accuracy])
                        # print('==>', _cost, _accuracy)
                except tf.errors.OutOfRangeError:
                    break
            print(np.mean(message, axis=0))

            message = []
            sess.run(test_iterator.initializer)
            while True:
                try:
                    window_batch, label_batch = sess.run(test_batch)
                    if window_batch.shape[0] == batch_size:
                        _, _cost, _accuracy = sess.run(
                            [Y_CNN_ADD_RNN, cost, accuracy], feed_dict={X: window_batch, Y: label_batch, KP: 0.5})
                        message.append([_cost, _accuracy])
                        # print('==>', _cost, _accuracy)
                except tf.errors.OutOfRangeError:
                    break
            print(np.mean(message, axis=0))
            print('>> train iter {0} done'.format(i + 1))


if __name__ == '__main__':
    main()
