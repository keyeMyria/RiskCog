import json
import logging
import os
from django import forms
from django.core.files.uploadedfile import UploadedFile as UploadedFileConverter
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.views.generic import View

from bin import tools
from bin.tools import make_dir
from models import UploadedFile, ModelBox
from riskserver import data_source
from riskserver import settings
from trainapp import queue_trainer
from trainapp.label import Label
from trainapp.tasks import train


class TrainForm(forms.Form):
    imei = forms.CharField()
    path = forms.FileField()


class UploadView(View):
    def get(self, request):
        uf = TrainForm()
        return render(request, 'register.html', {'uf': uf})

    def update_groud_id(self, user, state, group_size):
        """
        get a unique group id for a uploaded file

        :return: return a group id and a flag if this group is full
        """

        # current_max_group_id is like
        # {'current_max_group_id': 1} or {'current_max_group_id': None}
        # if lies, group id is 0
        current_max_group_id = UploadedFile.objects \
            .filter(type='train', user=user, state=state, is_lie=False) \
            .aggregate(current_max_group_id=Max('group_id'))['current_max_group_id']

        full = False
        if not current_max_group_id:
            new_group_id = 1
            if group_size == 1:
                full = True
        else:
            file_number = UploadedFile.objects \
                .filter(type='train', user=user, state=state, group_id=current_max_group_id).count()

            if file_number >= group_size:
                new_group_id = current_max_group_id + 1
            else:
                new_group_id = current_max_group_id
                if file_number == group_size - 1:
                    full = True
        return new_group_id, full

    def post(self, request):
        uf = TrainForm(request.POST, request.FILES)
        response_dict = {}
        if uf.is_valid():
            imei = uf.cleaned_data['imei']
            path = uf.cleaned_data['path']

            # get logger
            logger = logging.getLogger('rq.worker')

            # get user
            user = tools.get_or_create_user(imei)
            logger.info('get user {0} successfully'.format(imei))

            # group and save uploaded file
            # file check
            # here, I only use "django.core.files.uploadhandler.TemporaryFileUploadHandler"
            # to get a path but with a higher io cost.
            # it is reasonable to update 'check_sit_or_walk.exe' to support reading from MEMORY
            # and also, check_is_flat should be more compatible.
            # this tmp file will be remove after 'return'
            is_flat, state = tools.file_check(path.temporary_file_path())
            logger.info('check file successfully, is_flat: {0}, state: {1}'.format(is_flat, state))

            # get proper group id
            if is_flat:
                new_group_id = 0
            else:
                new_group_id, full = self.update_groud_id(user, state, data_source.TRAIN_FILE_GROUP_SIZE)

            # give a name
            file_name = tools.get_name()

            # convert
            # these two methods below are special
            # they both return a File object
            arff = tools.org_to_arff(path.temporary_file_path(), state)
            libsvm = tools.arff_to_svmlight(arff)
            logger.info('convert text file to arff and libsvm successfully')

            # save
            # change File to UploadedFile which can be stored automatically
            # paths are defined in model 'UploadedFile'
            arff = UploadedFileConverter(arff)
            libsvm = UploadedFileConverter(libsvm)
            this_file = UploadedFile.objects.create(
                user=user, path=path, arff_path=arff, libsvm_path=libsvm,
                file_name=file_name, group_id=new_group_id, type='train', is_lie=is_flat, state=state)
            # logger.info('save successfully, path is {0}'.format(this_file.path.path))
            logger.info('save successfully')

            # label
            # now, every file have a group_id and a state
            # next, label a group of files or one file
            # what we going to do is to give a label for every file
            # a label means a model box

            if new_group_id == data_source.LABEL_BEGIN:
                logger.info('first label begin')

                # label all files we have (the first time)
                files = UploadedFile.objects.filter(user=user, is_lie=False, type='train', state=state).all()
                label = Label(files, data_source.LABEL_TREE_DEPTH, data_source.LABEL_TREE_SKEWNESS)
                file_label_dict = label.get_file_label_dict()
                # create model box (only this time) and train
                for l, fs in file_label_dict.items():
                    # create model box dir
                    model_box_path = os.path.join(
                        settings.MODEL_BOX_ROOT, '{0}/{1}/{2}'.format(imei, state, l))
                    make_dir(model_box_path)
                    ModelBox.objects.create(user=user, state=state, model_box_order=l,
                                            model_box_path=model_box_path)
                    logger.info('create box {0} successfully'.format(l))
                    # update
                    for f in fs:
                        f.is_dispatched = True
                        f.target_model_box_order = int(l)
                        f.is_active = True
                        f.save()
                    # train
                    # when we train, give the files to be trained to 'train' method
                    train(user, fs, int(l), state)
                    logger.info('train box {0} successfully'.format(l))
                logger.info('first label end')
            elif new_group_id > data_source.LABEL_BEGIN:
                logger.info('normal label begin')

                label = Label(this_file)
                # wait until there are models in boxes
                target_model_box_order = label.dispatch(state)
                train_begin = False
                # update
                this_file.is_dispatched = True
                if target_model_box_order is not None:
                    this_file.target_model_box_order = target_model_box_order
                    this_file.is_active = True
                    train_begin = True
                    logger.info('target model box is {0}'.format(target_model_box_order))
                else:
                    logger.info('this file invalid')
                    this_file.target_model_box_order = 0
                    this_file.is_active = False
                this_file.save()

                # train mt
                if train_begin:
                    fs = UploadedFile.objects.filter(user=user, state=state,
                                                     target_model_box_order=target_model_box_order)
                    fs = list(fs)
                    fs.append(this_file)
                    # remove redundancy task
                    ids_removed = tools.clear_queue(user, len(fs), target_model_box_order, state)
                    logger.info('remove redundancy tasks successfully, remove {0}'.format(ids_removed))
                    logger.info('current size is {0}'.format(len(fs)))

                    queue_trainer.enqueue(train, user, fs,
                                          target_model_box_order, state,
                                          timeout=6000)
                    logger.info(
                        'enqueue successfully, state is {0}, target model is {1}'.format(state, target_model_box_order))
                logger.info('normal label end')
            else:
                logger.info('file is not enough, label begin at {0}, current is {1}'.format(data_source.LABEL_BEGIN,
                                                                                            new_group_id))
                pass

            # return
            # We should redefine these parameters used in the communication of phone and server,
            # because some of them are useless and meaningless.
            # imei, is_flat, state, result is OK.
            # required_files is meaningless, we can't figure out how many files totally we need for a box,
            # for the sake of semi-supervised system, we can just make sure how many valid files we need,
            # which is calculated by TRAIN_FILE_GROUP_SIZE * TRAINING_TIMES.
            # numsitarff and numwalkarff is not proper. After adding to the queue,  we just convert them to arff
            # from text.

            response_dict["imei"] = imei
            response_dict["is_flat"] = is_flat
            response_dict['state'] = state

            response_dict["required_files"] = data_source.sumfilesneed
            response_dict['numsitarff'] = UploadedFile.objects.filter(user=user, state='sit').count()
            response_dict['numwalkarff'] = UploadedFile.objects.filter(user=user, state='walk').count()

            response_dict["result"] = 0

            return HttpResponse(json.dumps(response_dict), content_type="application/json")
        else:
            return render(request, 'register.html', {'uf': uf})


def show_sensor_data(request, path):
    with open(os.path.join(settings.MEDIA_ROOT, path)) as f:
        lines = f.readlines()
        f.close()
    context = {'lines': lines}
    return render_to_response(template_name='sensor_data_detail.html', context=context)
