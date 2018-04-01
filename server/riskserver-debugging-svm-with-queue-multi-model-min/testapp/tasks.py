import logging
import subprocess
import tempfile
from django.core.exceptions import ObjectDoesNotExist

from bin.score import get_result
from bin.tools import count_lines
from riskserver import settings, data_source
from testapp.models import TestRecord
from trainapp.models import Model, ModelBox, UploadedFile


def test(test_user, target_user, state, group_id):
    """
    test
    """

    # prepare logger
    logger = logging.getLogger('rq.worker')

    test_imei = test_user.imei
    target_imei = target_user.imei

    logger.info('test begin, test_imei={0} state={1} group_id={2} target_imei={3}'.format(
        test_imei, state, group_id, target_imei))

    # prepare to test
    # get all model boxes by imei and state
    model_boxes = ModelBox.objects.filter(user=target_user, state=state).all()
    logger.info('get all model boxes for user {0} successfully, number of boxes is {1}'.format(
        target_imei, len(model_boxes)))

    # get all latest model in each model box
    latest_models = []
    for model_box in model_boxes:
        try:
            latest_model = Model.objects.get(user=target_user, model_box=model_box, model_latest=True)
            latest_models.append(latest_model)
        except ObjectDoesNotExist:
            continue
    logger.info('get all latest model successfully, number of models is {0}'.format(len(latest_models)))

    # if there is no model at all, just return 0, otherwise get the box-in accuracy
    model_exists = True
    if len(latest_models) == 0:
        model_exists = False

    # get the test file and check its validation
    test_file = UploadedFile.objects.get(user=test_user, type='test', group_id=group_id)
    libsvm = test_file.libsvm_path.path
    logger.info('get the test file {0} successfully'.format(group_id))

    is_valid = True
    if count_lines(libsvm) < data_source.TEST_MIN_NUMBER_OF_LINES:
        # test data is not enough
        is_valid = False
        logger.info('lines of this file {0} is not enough'.format(group_id))

    if model_exists:
        logger.info('svm predict begin')
        for latest_model in latest_models:
            temp_result = tempfile.NamedTemporaryFile(dir=settings.TEMP_ROOT)
            cmd = settings.BASE_DIR + '/bin/svm-predict -b 1' + ' ' \
                  + libsvm + ' ' + latest_model.model_path + ' ' + temp_result.name
            logger.info('execute cmd {0}'.format(cmd))
            p = subprocess.call(cmd, shell=True)  # block
            # temp_result.seek(0) # alter file pointer if you want read it directly
            res_acc, res_pre, res_rec = get_result(temp_result.name)
            logger.info('res_acc={0} res_pre={1} res_rec={2}'.format(res_acc, res_pre, res_rec))
            temp_result.close()  # auto delete
            # update the database
            TestRecord.objects.create(test_user=test_user, target_user=target_user, state=state, group_id=group_id,
                                      is_valid=is_valid, model_exists=model_exists,
                                      model_box_order=latest_model.model_box.model_box_order,
                                      model_order=latest_model.model_order,
                                      accuracy=res_acc, precision=res_pre, recall=res_rec)
        logger.info('svm predict end')
        logger.info('test successfully for the file {0}'.format(group_id))
    else:
        logger.info('model does not exist')
        TestRecord.objects.create(test_user=test_user, target_user=target_user, state=state, group_id=group_id,
                                  is_valid=is_valid, model_exists=model_exists)
        logger.info('failed test for the file {0}'.format(group_id))
