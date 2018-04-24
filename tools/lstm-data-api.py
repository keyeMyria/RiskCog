import os
import sys

import numpy as np
import tensorflow as tf


def input_pipeline(root, usage, batch_size=10, window_size=75, class_size=3):
    def _parse_function(example_proto):
        features = {'window/encoded': tf.VarLenFeature(tf.float32),
                    'window/label': tf.FixedLenFeature((), tf.int64, default_value=0)}
        parsed_features = tf.parse_single_example(example_proto, features)
        window = tf.reshape(tf.sparse_tensor_to_dense(parsed_features['window/encoded']), shape=(window_size, 9))
        label = tf.one_hot(parsed_features['window/label'], class_size)
        return window, label

    filenames = [os.path.join(root, usage, filename) for filename in os.listdir(os.path.join(root, usage))]

    dataset = tf.data.TFRecordDataset(filenames)
    dataset = dataset.map(_parse_function)
    dataset = dataset.batch(batch_size)
    iterator = dataset.make_initializable_iterator()

    return iterator, iterator.get_next()


class Config(object):
    def __init__(self, window_size=75, feature_size=9, class_size=10, epoch_size=1, batch_size=1024):
        # Input and recurrent
        self.batch_size = batch_size
        self.n_steps = window_size

        # Model save
        self.model_save_begin = 500

        # Training
        self.learning_rate = 0.0025
        self.lambda_loss_amount = 0.0015
        self.training_epochs = epoch_size

        # LSTM structure
        self.n_inputs = feature_size  # Features count is of 9: 3 * 3D sensors features over time
        self.n_hidden = 32  # nb of neurons inside the neural network
        self.n_layers = 1
        self.n_classes = class_size

        self.W = {
            'hidden': tf.Variable(tf.random_normal([self.n_inputs, self.n_hidden]), name='Wh'),
            'output': tf.Variable(tf.random_normal([self.n_hidden, self.n_classes]), name='Wo')
        }
        self.biases = {
            'hidden': tf.Variable(tf.random_normal([self.n_hidden], mean=1.0), name='biah'),
            'output': tf.Variable(tf.random_normal([self.n_classes]), name='biao')
        }


def LSTM_Network(_X, config):
    '''Function returns a TensorFlow RNN with two stacked LSTM cells

    Two LSTM cells are stacked which adds deepness to the neural network.
    Note, some code of this notebook is inspired from an slightly different
    RNN architecture used on another dataset, some of the credits goes to
    'aymericdamien'.

    Args:
        _X:     ndarray feature matrix, shape: [batch_size, time_steps, n_inputs]
        config: Config for the neural network.

    Returns:
        This is a description of what is returned.

    Raises:
        KeyError: Raises an exception.

      Args:
        feature_mat: ndarray fature matrix, shape=[batch_size,time_steps,n_inputs]
        config: class containing config of network
      return:
              : matrix  output shape [batch_size,n_classes]
    '''
    # (NOTE: This step could be greatly optimised by shaping the dataset once
    # input shape: (batch_size, n_steps, n_input)
    _X = tf.transpose(_X, [1, 0, 2])  # permute n_steps and batch_size
    # Reshape to prepare input to hidden activation
    _X = tf.reshape(_X, [-1, config.n_inputs])
    # new shape: (n_steps*batch_size, n_input)

    # Linear activation
    _X = tf.nn.relu(tf.matmul(_X, config.W['hidden']) + config.biases['hidden'])
    # Split data because rnn cell needs a list of inputs for the RNN inner loop
    _X = tf.split(_X, config.n_steps, 0)

    # new shape: n_steps * (batch_size, n_hidden)

    # Define two stacked LSTM cells (two recurrent layers deep) with tensorflow
    lstm_cell_1 = tf.contrib.rnn.BasicLSTMCell(config.n_hidden, forget_bias=1.0, state_is_tuple=True)
    lstm_cell_2 = tf.contrib.rnn.BasicLSTMCell(config.n_hidden, forget_bias=1.0, state_is_tuple=True)
    lstm_cells = tf.contrib.rnn.MultiRNNCell([lstm_cell_1] * config.n_layers, state_is_tuple=True)
    # Get LSTM cell output
    outputs, states = tf.contrib.rnn.static_rnn(lstm_cells, _X, dtype=tf.float32)

    # Get last time step's output feature for a 'many to one' style classifier,
    # as in the image describing RNNs at the top of this page
    lstm_last_output = outputs[-1]

    # Linear activation
    return tf.matmul(lstm_last_output, config.W['output']) + config.biases['output']


# @profile
def main():
    # -----------------------------------
    # Step 1: define parameters for model
    # -----------------------------------
    DATA_PATH = 'tfrecord-for-10-2000'
    config = Config(window_size=75, feature_size=9, class_size=10, epoch_size=500, batch_size=1500)
    # ------------------------------------------------------
    # Step 2: build the neural network
    # ------------------------------------------------------
    X = tf.placeholder(tf.float32, [None, config.n_steps, config.n_inputs])
    Y = tf.placeholder(tf.float32, [None, config.n_classes])

    pred_Y = LSTM_Network(X, config)

    # Loss,optimizer,evaluation
    l2 = config.lambda_loss_amount * \
         sum(tf.nn.l2_loss(tf_var) for tf_var in tf.trainable_variables())
    # Softmax loss and L2
    cost = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(labels=Y, logits=pred_Y)) + l2
    optimizer = tf.train.AdamOptimizer(
        learning_rate=config.learning_rate).minimize(cost)

    correct_pred = tf.equal(tf.argmax(pred_Y, 1), tf.argmax(Y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_pred, dtype=tf.float32))
    # -----------------------------------
    # Step 3: define an input pipeline
    # -----------------------------------
    train_iterator, train_batch = input_pipeline(
        root=DATA_PATH, usage='train', batch_size=config.batch_size, class_size=config.n_classes)
    test_iterator, test_batch = input_pipeline(
        root=DATA_PATH, usage='test', batch_size=config.batch_size, class_size=config.n_classes)
    # --------------------------------------------
    # Step 4: train the neural network with an input pipeline
    # --------------------------------------------
    # saver = tf.train.Saver()  # generate saver, to save the parameter

    with tf.Session() as sess:
        sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])

        for i in range(0, config.training_epochs):
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
                        [pred_Y, cost, accuracy], feed_dict={X: window_batch, Y: label_batch})
                    message.append([_cost, _accuracy])
                except tf.errors.OutOfRangeError:
                    break
            print(np.mean(message, axis=0))

            print('>> train iter {0} done'.format(i+1))

if __name__ == '__main__':
    main()
