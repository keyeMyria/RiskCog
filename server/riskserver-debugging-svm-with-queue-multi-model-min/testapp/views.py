import json
import logging
from django import forms
from django.core.files.uploadedfile import UploadedFile as UploadedFileConverter
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from bin import tools
from testapp.tasks import test
from trainapp.models import UploadedFile


# Create your views here.

class TestForm(forms.Form):
    test_imei = forms.CharField()
    target_imei = forms.CharField()
    path = forms.FileField()


class TestView(View):
    def get(self, request):
        uf = TestForm()
        return render(request, 'register.html', {'uf': uf})

    def post(self, request):
        uf = TestForm(request.POST, request.FILES)
        if uf.is_valid():
            test_imei = uf.cleaned_data['test_imei']
            target_imei = uf.cleaned_data['target_imei']
            path = uf.cleaned_data['path']

            # get logger
            logger = logging.getLogger('rq.worker')
            logger.info('test imei is {0}, target imei is {1}'.format(test_imei, target_imei))

            # get the test_user's information
            test_user = tools.get_or_create_user(test_imei, create=False)
            target_user = tools.get_or_create_user(target_imei, create=False)
            logger.info('get test_user {0} successfully'.format(test_imei))

            # file check
            is_flat, state = tools.file_check(path.temporary_file_path())
            logger.info('check file successfully, is_flat: {0}, state: {1}'.format(is_flat, state))

            # get proper group id
            # when you test, there is no need to group these files
            # so just assign the count of them as the group_id
            is_active = True
            if is_flat:
                new_group_id = 0
                is_active = False
            else:
                new_group_id = UploadedFile.objects.filter(user=test_user, type='test', is_lie=False).count() + 1

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
                user=test_user, path=path, arff_path=arff, libsvm_path=libsvm,
                file_name=file_name, group_id=new_group_id, type='test',
                is_lie=is_flat, state=state, is_active=is_active)
            # logger.info('save successfully, path is {0}'.format(this_file.path.path))
            logger.info('save successfully')

            # test
            # queue_tester.enqueue(test, imei, state, new_group_id)
            if not is_flat:
                test(test_user, target_user, state, new_group_id)

            # get the number of test files which have been uploaded
            response_dict = {'max_version': new_group_id}
            return HttpResponse(json.dumps(response_dict), content_type="application/json")
        else:
            return render(request, 'register.html', {'uf': uf})
