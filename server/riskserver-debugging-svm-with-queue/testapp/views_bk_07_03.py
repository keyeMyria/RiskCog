import os
import time
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response

from riskserver import settings
from testapp.models import Test
from testapp.parse import parse_data
from testapp.score import get_accuracy
from trainapp.check import check_is_lie
from trainapp.tools import get_dir_file_number, remove_file
from trainapp.views import parse_data_by_path


# Create your views here.

class TestForm(forms.Form):
    imei = forms.CharField()
    path = forms.FileField()


def register(request):
    if request.method == "POST":
        uf = TestForm(request.POST, request.FILES)
        if uf.is_valid():

            imei = uf.cleaned_data['imei']
            path = uf.cleaned_data['path']
            result_dir = os.path.join(settings.BASE_DIR, "result", imei)
            file_cnt = get_dir_file_number(result_dir) / 2
            target_summary_file = os.path.join(result_dir, "summary_" + file_cnt + ".txt")
            remove_file(target_summary_file)
            remove_file(os.path.join(result_dir, "results.txt"))

            ISOTIMEFORMAT = '%Y%m%d%H%M%S'
            name = str(time.strftime(ISOTIMEFORMAT))
            dest_dir = os.path.join(settings.BASE_DIR, "media", "test", imei)
            dest_name = os.path.join(dest_dir, name)
            handle_uploaded_file(path, imei, dest_name)

            is_lie = check_is_lie(dest_name)
            if not is_lie:
                test = Test()
                test.imei = imei
                test.path = dest_name
                test.save()
            else:
                # here need return a JSON lie
                if os.path.exists(dest_name):
                    os.remove(dest_name)

            res1 = solve_state(result_dir, imei, 'sit', dest_name)
            res2 = solve_state(result_dir, imei, 'walk', dest_name)
            res = max(res1, res2)

            fp = open(target_summary_file, "w")
            fp.write(str(res))
            fp.close()

            # add test file to train
            target_train_dir = os.path.join(settings.BASE_DIR, "media", "train", imei)
            target_train_file = os.path.join(target_train_dir, name)
            if not os.path.exists(target_train_dir):
                os.makedirs(target_train_dir)
            if not os.path.exists(target_train_file) or (
                os.path.exists(target_train_file) and os.path.getsize(target_train_file) != os.path.getsize(dest_name)):
                open(target_train_file, "wb").write(open(dest_name, "rb").read())

            number = parse_data_by_path(target_train_dir, imei)
            print "sit  result  = " + str(res1)
            print "walk result  = " + str(res2)
            #			return HttpResponse('upload ok! ' + str(number) +' files. in '+ imei+'.')
            return_res = {'max_version': file_cnt}
            return HttpResponse(json.dumps(return_res), content_type="application/json")

    else:
        uf = TestForm()

    return render_to_response('register.html', {'uf': uf})


def solve_state(result_dir, imei, state, dest_name):
    create_path(result_dir)
    vw_path = os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.vw")
    data_set = parse_data(imei, dest_name)
    result_path = os.path.join(result_dir, "results.txt_" + state)

    if not os.path.exists(vw_path):
        return 0

    output = os.popen("vw -d " + data_set + " -t -i " + vw_path + " -p " + result_path)
    print output.read()

    res = get_accuracy(data_set, result_path)
    print " tttt"
    #			remove_file(result_path)
    return res;


def handle_uploaded_file(f, imei, dest_name):
    tmp_path = os.path.join(settings.BASE_DIR, "media", "test", imei)
    if os.path.isdir(tmp_path):
        pass
    else:
        os.makedirs(tmp_path)

    dest = open(dest_name, "wb+")
    for chunk in f.chunks():
        dest.write(chunk)
    dest.close()


def create_path(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)
