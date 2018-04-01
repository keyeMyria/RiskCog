import json
import logging
from django import forms
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from bin import tools
from query.models import Score
from testapp.models import TestRecord
from trainapp.models import ModelBox, Model


class QueryForm(forms.Form):
    test_imei = forms.CharField()
    target_imei = forms.CharField()
    version = forms.CharField()


class QueryView(View):
    def get(self, request):
        uf = QueryForm()
        return render(request, 'register.html', {'uf': uf})

    def post(self, request):
        uf = QueryForm(request.POST)
        if uf.is_valid():
            test_imei = uf.cleaned_data['test_imei']
            target_imei = uf.cleaned_data['target_imei']
            version = uf.cleaned_data['version']

            # get logger
            logger = logging.getLogger('rq.worker')
            logger.info('query test imei is {0}, target imei is {1}'.format(test_imei, target_imei))

            sit_acc, walk_acc, sit_pre, walk_pre, sit_rec, walk_rec = .0, .0, .0, .0, .0, .0,
            sit_model_exists, walk_model_exists, is_sit = False, False, False

            # get the test_user's information
            test_user = tools.get_or_create_user(test_imei, create=False)
            target_user = tools.get_or_create_user(target_imei, create=False)
            logger.info('get test_user {0} successfully'.format(test_imei))

            # score
            accuracy_f = score_2(test_user, target_user, version)
            Score.objects.create(test_user=test_user, target_user=target_user, version=version, accuracy=accuracy_f)

            result = {'accuracy': accuracy_f}
            response_dict = {'result': result, 'version': version}
            return HttpResponse(json.dumps(response_dict), content_type="application/json")
        else:
            return render(request, 'register.html', {'uf': uf})


def score_1(user, records):
    N = 0
    W = []
    A = []
    for record in records:
        if float(record.accuracy) != 0:
            # get the model_order of current record
            model_box_order = record.model_box_order
            state = record.state
            model_box = ModelBox.objects.get(user=user, state=state, model_box_order=model_box_order)
            model = Model.objects.get(user=user, model_box=model_box, model_latest=True)
            model_order = model.model_order
            if model_order >= 5:
                W.append(model_order)
                # get the accuracy
                accuracy = float(record.accuracy)
                A.append(accuracy)
                N += model_order
                # print
                print model_order, accuracy

    for i in range(0, len(W)):
        W[i] /= float(N)

    accuracy_f = .0
    for i in range(0, len(W)):
        accuracy_f += A[i] * W[i]
    print N, accuracy_f

    return accuracy_f


def score_2(test_user, target_user, version):
    # get all test records and find the max accuracy for each group
    # {'accuracy_max': None}
    accuracy_max = TestRecord.objects.filter(test_user=test_user, target_user=target_user, group_id=version) \
        .aggregate(accuracy_max=Max('accuracy'))
    accuracy_max = accuracy_max['accuracy_max']

    if accuracy_max is None:
        return 0
    else:
        test_record = TestRecord.objects.filter(test_user=test_user, target_user=target_user, group_id=version,
                                                accuracy=accuracy_max)[0]
        return test_record.accuracy
