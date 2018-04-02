"""
unittest for one_class_svm.py
"""
import unittest
import one_class_svm
import os
import numpy as np

DATASET = 'dataset'


class OneClassSVMTestCase(unittest.TestCase):
    def test_preprocessing(self):
        os.system('rm -rf {0}'.format(DATASET))
        os.system('mkdir -p {0}'.format(DATASET))
        self.assertRaises(ValueError, one_class_svm.preprocessing, DATASET)
        # only train but is not enough
        os.system('mkdir -p {0}/train/user'.format(DATASET))
        for i in range(0, 9):
            os.system('touch {1}/train/user/file{0}'.format(i, DATASET))
        self.assertRaises(ValueError, one_class_svm.preprocessing, DATASET)
        # only train but is enough
        for i in range(9, 100):
            os.system('touch {1}/train/user/file{0}'.format(i, DATASET))
        training_set, validation_set, testing_set, other_set = one_class_svm.preprocessing(DATASET)
        self.assertEqual(100, len(training_set) + len(validation_set) + len(testing_set))
        self.assertEqual(80, len(training_set))
        self.assertEqual(10, len(validation_set))
        self.assertEqual(10, len(testing_set))
        self.assertIsNone(other_set)
        # train and test
        os.system('mkdir -p {0}/test/user'.format(DATASET))
        for i in range(0, 10):
            os.system('touch {1}/test/user/file{0}'.format(i, DATASET))
        training_set, validation_set, testing_set, other_set = one_class_svm.preprocessing(DATASET)
        self.assertEqual(100, len(training_set) + len(validation_set))
        self.assertEqual(80, len(training_set))
        self.assertEqual(20, len(validation_set))
        self.assertEqual(10, len(testing_set))
        self.assertIsNone(other_set)
        # train, test and other
        os.system('mkdir -p {0}/other/user'.format(DATASET))
        for i in range(0, 10):
            os.system('touch {1}/other/user/file{0}'.format(i, DATASET))
        _, _, _, other_set = one_class_svm.preprocessing(DATASET)
        self.assertEqual(10, len(other_set))
        # multiple users
        os.system('mkdir -p {0}/train/user2'.format(DATASET))
        for i in range(0, 9):
            os.system('touch {1}/train/user2/file{0}'.format(i, DATASET))
        self.assertRaises(ValueError, one_class_svm.preprocessing, DATASET)
        for i in range(9, 100):
            os.system('touch {1}/train/user2/file{0}'.format(i, DATASET))
        training_set, validation_set, testing_set, other_set = one_class_svm.preprocessing(DATASET)
        self.assertEqual(200, len(training_set) + len(validation_set))
        self.assertEqual(160, len(training_set))
        self.assertEqual(40, len(validation_set))
        self.assertEqual(10, len(testing_set))
        # check filepath
        root, type_, user, filename = training_set[0].split('/')
        self.assertEqual(DATASET, root)
        self.assertIn(type_, ['train', 'test', 'other'])
        self.assertIn(user, ['user1', 'user2'])
        os.system('rm -rf {0}'.format(DATASET))

    def test_train_and_predict(self):
        os.system('rm -rf {0}'.format(DATASET))
        np.random.seed(0)
        # train
        test_data = np.random.randn(9 * 20, 1)  # 2 windows in total
        os.system('mkdir -p {0}/train/user'.format(DATASET))
        os.system('mkdir -p {0}/train/user2'.format(DATASET))
        np.savetxt('{0}/train/user/test_data'.format(DATASET), test_data, fmt='%1.4e')
        np.savetxt('{0}/train/user/test_data2'.format(DATASET), test_data, fmt='%1.4e')
        np.savetxt('{0}/train/user2/test_data'.format(DATASET), test_data, fmt='%1.4e')
        # test
        test_data = np.random.randn(9 * 20, 1)  # 2 windows in total
        os.system('mkdir -p dataset/test/user')
        os.system('mkdir -p dataset/test/user2')
        np.savetxt('{0}/test/user/test_data'.format(DATASET), test_data, fmt='%1.4e')
        np.savetxt('{0}/test/user/test_data2'.format(DATASET), test_data, fmt='%1.4e')
        np.savetxt('{0}/test/user2/test_data'.format(DATASET), test_data, fmt='%1.4e')
        model_paths = one_class_svm.train(DATASET, ['{0}/train/user/test_data'.format(DATASET),
                                                    '{0}/train/user/test_data2'.format(DATASET),
                                                    '{0}/train/user2/test_data'.format(DATASET)], [])
        test_data = np.loadtxt('{0}/train/user/test_data.arff'.format(DATASET))
        self.assertEqual((2, 64), test_data.shape)
        test_data = np.loadtxt('{0}/train/user/test_data.arff.libsvm'.format(DATASET), delimiter='   ',
                               dtype=np.string_)
        self.assertEqual((2, 63), test_data.shape)  # remove state
        test_data = np.loadtxt('{0}/train/user/user.arff.libsvm'.format(DATASET), delimiter='   ', dtype=np.string_)
        self.assertEqual((4, 63), test_data.shape)  # append
        test_data = np.loadtxt('{0}/train/user2/user2.arff.libsvm'.format(DATASET), delimiter='   ', dtype=np.string_)
        self.assertEqual((2, 63), test_data.shape)  # append
        model = np.loadtxt('{0}/model/user/user.model'.format(DATASET), delimiter='\n', dtype=np.string_)
        self.assertEqual(9, model.shape[0])
        model = np.loadtxt('{0}/model/user2/user2.model'.format(DATASET), delimiter='\n', dtype=np.string_)
        self.assertEqual(9, model.shape[0])
        self.assertEqual(2, len(model_paths))

        accuracies = one_class_svm.predict(DATASET, ['{0}/model/user/user.model'.format(DATASET)],
                                           ['{0}/test/user/test_data'.format(DATASET),
                                            '{0}/test/user/test_data2'.format(DATASET)])
        self.assertEqual(2, len(accuracies))
        os.system('rm -rf {0}'.format(DATASET))
