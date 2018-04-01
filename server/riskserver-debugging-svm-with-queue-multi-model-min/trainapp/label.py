import os
import subprocess
import tempfile
from django.core.exceptions import ObjectDoesNotExist

import numpy as np
from sklearn.cluster import KMeans

from bin import tools
from bin.score import get_result
from riskserver import settings, data_source
from trainapp.models import ModelBox, Model, BoxDispatchingCheckAccuracy, UploadedFile


class Label:
    def __init__(self, file, depth=3, skewness=2):
        self._file = file
        self._depth = depth
        self._skewness = skewness
        self._label_groups = []
        self._sensor_data_vector = []
        self._state = None
        self._flag = 'multiple'

        if not isinstance(self._file, UploadedFile):
            paths = [os.path.join(settings.BASE_DIR, file[i].path.path) for i in range(0, len(file))]
            self._sensor_data_vector = tools.get_sensor_vector(paths)
            self._label_core(self._sensor_data_vector, [i for i in range(0, len(self._sensor_data_vector))],
                             self._depth, self._skewness)
        else:
            self._flag = 'single'
            self._state = self._file.state

    def _label_core(self, vectors_all, indices, depth=3, skewness=3):
        """
        return indices grouped by same label recursively (binary tree)

        which is a list like [[1, 2], [3, 4], [5]]

        :param vectors_all: vectors of files you want to label, make sure its order is same to these files
        :param indices: has to be initially like [i for i in range(0, len(vectors_all)]
        :param labels: store the results
        :param skewness: max skewness of child trees
        :param depth: max depth of recursion, default=3
        :return: return indices grouped by same label recursively (binary tree)
        """

        # label
        vectors = [vectors_all[i] for i in indices]
        kmeans = KMeans(n_clusters=2)
        kmeans.fit(np.array(vectors))
        labels = np.array(kmeans.labels_)

        # get indices of two parts
        indices_left = []
        indices_right = []
        for i in range(0, len(labels)):
            if labels[i] == 0:
                indices_right.append(indices[i])
            elif labels[i] == 1:
                indices_left.append(indices[i])
            else:
                pass

        if depth == 1:
            self._label_groups.append(indices_left)
            self._label_groups.append(indices_right)
            return

        # calculate the skewness
        l_path_left = len(indices_left)
        l_path_right = len(indices_right)

        if l_path_left >= l_path_right:
            p = l_path_left / l_path_right
            self._label_groups.append(indices_right)
            if p >= skewness:
                # deeper cluster
                self._label_core(vectors_all, indices_left, depth - 1, skewness)
            else:
                self._label_groups.append(indices_left)
        else:
            p = l_path_right / l_path_left
            self._label_groups.append(indices_left)
            if p >= skewness:
                # deeper cluster
                self._label_core(vectors_all, indices_right, depth - 1, skewness)
            else:
                self._label_groups.append(indices_right)
        return

    def get_file_label_dict(self):
        labels = [i for i in range(0, len(self._label_groups))]
        file_label_dict = {}
        for i in range(0, len(labels)):
            file_label_dict['{0}'.format(i + 1)] = [self._file[j] for j in self._label_groups[i]]
        return file_label_dict

    def dispatch(self, state):
        if not self._flag == 'single':
            raise ValueError('Please pass more than one file')

        libsvm_full_path = os.path.join(settings.BASE_DIR, self._file.libsvm_path.path)

        user = self._file.user
        group_id = self._file.group_id

        # get boxes first and next get all latest models
        # model_boxes is like
        # [<ModelBox: description>, <ModelBox: *>, <ModelBox: *>]
        model_boxes = ModelBox.objects.filter(user=user, state=state).all()

        # latest_model will be like
        # [<Model: description>, None]
        latest_models = []
        for model_box in model_boxes:
            try:
                latest_model = Model.objects.get(user=user, model_box=model_box, model_latest=True)
                latest_models.append(latest_model)
            except ObjectDoesNotExist:
                return None

        # let us begin the test
        bd_checks = []
        for latest_model in latest_models:
            temp_result = tempfile.NamedTemporaryFile(dir=settings.TEMP_ROOT)
            cmd = settings.BASE_DIR + '/bin/svm-predict -b 1' + ' ' \
                  + libsvm_full_path + ' ' + latest_model.model_path + ' ' + temp_result.name
            p = subprocess.call(cmd, shell=True)  # block
            # temp_result.seek(0) # alter file pointer if you want read it directly
            res_acc, res_pre, res_rec = get_result(temp_result.name)
            temp_result.close()  # auto delete

            # update the information(which files test which box)
            # we will add a record to describe whether these files should be put into this box or not next
            bd_check = BoxDispatchingCheckAccuracy.objects.create(
                model_box=latest_model.model_box,
                file=self._file,
                accuracy=res_acc,
            )
            bd_checks.append(bd_check)

        # get the target record
        target = None
        for bd_check in bd_checks:
            if target is None:
                target = bd_check
            else:
                if bd_check.accuracy >= target.accuracy:
                    target = bd_check

        accuracy_max = target.accuracy

        # calculate the acceptance accuracy
        factor = 1
        if accuracy_max < data_source.BOX_IN_ACCURACY_LOWER * factor:
            # other
            return None
        else:
            target_model_box_order = target.model_box.model_box_order

        # check times to be trained before new training pulse
        times = UploadedFile.objects.filter(user=user, state=state, target_model_box_order=target_model_box_order,
                                              is_dispatched=True, is_trained=True, is_active=True).count()
        if times > data_source.TRAINING_TIME:
            return None

        return target_model_box_order
