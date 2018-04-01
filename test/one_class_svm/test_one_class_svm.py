"""
unittest for one_class_svm.py
"""
import unittest
import one_class_svm
import os
import numpy as np


class OneClassSVMTestCase(unittest.TestCase):
    def test_preprocessing(self):
        os.system('rm -rf dataset')
        os.system('mkdir -p dataset')
        self.assertRaises(ValueError, one_class_svm.preprocessing, 'dataset')
        # only train but is not enough
        os.system('mkdir -p dataset/train/user')
        for i in range(0, 9):
            os.system('touch dataset/train/user/file{0}'.format(i))
        self.assertRaises(ValueError, one_class_svm.preprocessing, 'dataset')
        # only train but is enough
        for i in range(9, 100):
            os.system('touch dataset/train/user/file{0}'.format(i))
        training_set, validation_set, testing_set, other_set = one_class_svm.preprocessing('dataset')
        self.assertEqual(100, len(training_set) + len(validation_set) + len(testing_set))
        self.assertEqual(80, len(training_set))
        self.assertEqual(10, len(validation_set))
        self.assertEqual(10, len(testing_set))
        self.assertIsNone(other_set)
        # train and test
        os.system('mkdir -p dataset/test/user')
        for i in range(0, 10):
            os.system('touch dataset/test/user/file{0}'.format(i))
        training_set, validation_set, testing_set, other_set = one_class_svm.preprocessing('dataset')
        self.assertEqual(100, len(training_set) + len(validation_set))
        self.assertEqual(80, len(training_set))
        self.assertEqual(20, len(validation_set))
        self.assertEqual(10, len(testing_set))
        self.assertIsNone(other_set)
        # train, test and other
        os.system('mkdir -p dataset/other/user')
        for i in range(0, 10):
            os.system('touch dataset/other/user/file{0}'.format(i))
        _, _, _, other_set = one_class_svm.preprocessing('dataset')
        self.assertEqual(10, len(other_set))
        # multiple users
        os.system('mkdir -p dataset/train/user2')
        for i in range(0, 9):
            os.system('touch dataset/train/user2/file{0}'.format(i))
        self.assertRaises(ValueError, one_class_svm.preprocessing, 'dataset')
        for i in range(9, 100):
            os.system('touch dataset/train/user2/file{0}'.format(i))
        training_set, validation_set, testing_set, other_set = one_class_svm.preprocessing('dataset')
        self.assertEqual(200, len(training_set) + len(validation_set))
        self.assertEqual(160, len(training_set))
        self.assertEqual(40, len(validation_set))
        self.assertEqual(10, len(testing_set))
        # check filepath
        root, type_, user, filename = training_set[0].split('/')
        self.assertEqual('dataset', root)
        self.assertIn(type_, ['train', 'test', 'other'])
        self.assertIn(user, ['user1', 'user2'])
        os.system('rm -rf dataset')

    def test_train_and_predict(self):
        os.system('rm -rf dataset')
        np.random.seed(0)
        # train
        test_data = np.random.randn(9 * 20, 1) # 2 windows in total
        os.system('mkdir -p dataset/train/user')
        os.system('mkdir -p dataset/train/user2')
        np.savetxt('dataset/train/user/test_data', test_data, fmt='%1.4e')
        np.savetxt('dataset/train/user/test_data2', test_data, fmt='%1.4e')
        np.savetxt('dataset/train/user2/test_data', test_data, fmt='%1.4e')
        # test
        test_data = np.random.randn(9 * 20, 1) # 2 windows in total
        os.system('mkdir -p dataset/test/user')
        os.system('mkdir -p dataset/test/user2')
        np.savetxt('dataset/test/user/test_data', test_data, fmt='%1.4e')
        np.savetxt('dataset/test/user/test_data2', test_data, fmt='%1.4e')
        np.savetxt('dataset/test/user2/test_data', test_data, fmt='%1.4e')
        model_paths = one_class_svm.train('dataset', ['dataset/train/user/test_data', 'dataset/train/user/test_data2',
                             'dataset/train/user2/test_data'], [])
        test_data = np.loadtxt('dataset/train/user/test_data.arff')
        self.assertEqual((2, 64), test_data.shape)
        test_data = np.loadtxt('dataset/train/user/test_data.arff.libsvm', delimiter='   ', dtype=np.string_)
        self.assertEqual((2, 63), test_data.shape) # remove state
        test_data = np.loadtxt('dataset/train/user/user.arff.libsvm', delimiter='   ', dtype=np.string_)
        self.assertEqual((4, 63), test_data.shape) # append
        test_data = np.loadtxt('dataset/train/user2/user2.arff.libsvm', delimiter='   ', dtype=np.string_)
        self.assertEqual((2, 63), test_data.shape) # append
        model = np.loadtxt('dataset/model/user/user.model', delimiter='\n', dtype=np.string_)
        self.assertEqual(9, model.shape[0])
        model = np.loadtxt('dataset/model/user2/user2.model', delimiter='\n', dtype=np.string_)
        self.assertEqual(9, model.shape[0])
        self.assertEqual(2, len(model_paths))

        accuracies = one_class_svm.predict('dataset', ['dataset/model/user/user.model'],
                                           ['dataset/test/user/test_data', 'dataset/test/user/test_data2'])
        self.assertEqual(2, len(accuracies))
        os.system('rm -rf dataset')
