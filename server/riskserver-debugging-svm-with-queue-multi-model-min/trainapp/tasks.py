import logging
import os
import subprocess
import tempfile

from bin.arff2libsvm import arff2svmlight
from bin.tools import list_files
from models import Model, ModelBox
from models import UploadedFile
from riskserver import data_source
from riskserver import settings


def train(user, files_to_be_trained, target_model_box_order, state):
    """
    trainer called when a dispatch is successful

    """
    imei = user.imei

    # prepare logger
    logger = logging.getLogger('rq.worker')

    # We should label other files of this user as -1
    all_files = UploadedFile.objects.filter(
        user=user, is_lie=False, is_active=True, is_dispatched=True, is_trained=False)
    files_relabeled = []
    for file in all_files:
        if file not in files_to_be_trained:
            files_relabeled.append(file)

    temp_arff_file_list_for_yourself = tempfile.NamedTemporaryFile(dir=settings.TEMP_ROOT, suffix='.list', delete=False)
    for file_to_be_trained in files_to_be_trained:
        full_path = file_to_be_trained.arff_path.path
        temp_arff_file_list_for_yourself.write('{0}\n'.format(full_path))
    logger.info('list arff file for yourself successfully')

    # list arff files for others
    temp_arff_file_list_for_others = tempfile.NamedTemporaryFile(dir=settings.TEMP_ROOT, delete=False, suffix='.list')
    list_files(data_source.Other_users_path, state, temp_arff_file_list_for_others.name)
    for file_relabeled in files_relabeled:
        temp_arff_file_list_for_others.write('{0}\n'.format(file_relabeled.arff_path.path))
    logger.info('list arff file for others successfully')

    # make 1:5
    temp_pick_up_arff = tempfile.NamedTemporaryFile(dir=settings.TEMP_ROOT, suffix='.pick_up_arff', delete=False)
    # you have to add one line code below so that sector.py can read the content in temp_arff_file_list_for_yourself
    temp_arff_file_list_for_yourself.seek(0)

    cmd = settings.BASE_DIR + '/bin/sector.py' + ' ' + imei + ' ' + str(data_source.RATIO) + ' ' \
          + temp_arff_file_list_for_yourself.name + ' ' + temp_arff_file_list_for_others.name
    logger.info('execute {0}'.format(cmd))
    p = subprocess.call(cmd, shell=True, stdout=open(temp_pick_up_arff.name, 'a'))
    logger.info('pick up files by 1:{0} successfully'.format(data_source.RATIO))

    # remove the temp files
    temp_arff_file_list_for_others.close()
    temp_arff_file_list_for_yourself.close()
    os.remove(temp_arff_file_list_for_others.name)
    os.remove(temp_arff_file_list_for_yourself.name)  # not semi supervised system
    logger.info('normal train system begin')

    # convert arff -> libsvm
    temp_pick_up_libsvm = tempfile.NamedTemporaryFile(dir=settings.TEMP_ROOT, delete=False)
    arff2svmlight(temp_pick_up_arff.name, temp_pick_up_libsvm.name)
    temp_pick_up_arff.close()
    os.remove(temp_pick_up_arff.name)
    logger.info('make train set successfully')

    # train
    # model box exists (created before 'train' being called in 'dispatch')
    target_model_box = ModelBox.objects.get(user=user, state=state, model_box_order=target_model_box_order)
    # TODO needs a universe id dispatcher in multi-threading
    # target_model_order = Model.objects.filter(user=user, model_box=target_model_box).count() + 1
    target_model_order = len(files_to_be_trained)

    temp_model = tempfile.NamedTemporaryFile(dir=settings.TEMP_ROOT, delete=False)
    cmd = 'bin/svm-train -s 0 -t 2 -d 3 -g 0 -r 0 -c 5000 -n 0.5 -p 0.1 -h 1 -b 1' + \
          ' ' + temp_pick_up_libsvm.name + ' ' + temp_model.name
    logger.info('execute {0}'.format(cmd))
    p = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)  # block

    # save this model
    # the dir of this model exists (created before 'train' being called in 'dispatch')
    # TODO find a way to save the temporary file directly
    target_model_path = os.path.join(target_model_box.model_box_path, '{0}.model'.format(str(target_model_order)))

    with open(target_model_path, 'w') as f:
        temp_model.seek(0)
        f.write(temp_model.read())
        f.close()
    temp_model.close()
    temp_pick_up_libsvm.close()
    os.remove(temp_model.name)
    os.remove(temp_pick_up_libsvm.name)
    logger.info('normal train successfully, target model path is {0}'.format(target_model_path))

    # update this model in database and the latest flag
    Model.objects.filter(user=user, model_box=target_model_box).update(model_latest=False)
    Model.objects.create(user=user, model_box=target_model_box, model_path=target_model_path,
                         is_active=True, model_order=target_model_order, model_latest=True)
    # update uploaded file
    for file_to_be_trained in files_to_be_trained:
        file_to_be_trained.is_trained = True
        file_to_be_trained.target_model_order = target_model_order
        file_to_be_trained.save()
    logger.info('train successfully')

    return 0
