import os
import time
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response

from riskserver import data_source
from riskserver import settings
from trainapp.check import check_is_lie
from trainapp.models import Train
from trainapp.parse import parse_data


# Create your views here.

class TrainForm(forms.Form):
    imei = forms.CharField()
    path = forms.FileField()


def register(request):
    if request.method == "POST":
        uf = TrainForm(request.POST, request.FILES)
        if uf.is_valid():
            imei = uf.cleaned_data['imei']
            path = uf.cleaned_data['path']
            ISOTIMEFORMAT = '%Y%m%d%H%M%S'
            name = str(time.strftime(ISOTIMEFORMAT))
            dest_dir = os.path.join(settings.BASE_DIR, "media", "train", imei)
            dest_name = os.path.join(dest_dir, name)
            handle_uploaded_file(path, imei, dest_name)

            # check for invalid datasets
            is_lie = check_is_lie(dest_name)
            if not is_lie:
                train = Train()
                train.imei = imei
                train.path = dest_name
                train.save()
            else:
                if os.path.exists(dest_name):
                    os.remove(dest_name)

                    # check whether there is enought dataset to train
            number = parse_data_by_path(dest_dir, imei)
            return HttpResponse('upload ok! ' + str(number) + ' files. in ' + imei + '.')
    else:
        uf = TrainForm()

    return render_to_response('register.html', {'uf': uf})


def handle_uploaded_file(f, imei, dest_name):
    tmp_path = os.path.join(settings.BASE_DIR, "media", "train", imei)
    if os.path.isdir(tmp_path):
        pass
    else:
        os.makedirs(tmp_path)

    dest = open(dest_name, "wb+")
    for chunk in f.chunks():
        dest.write(chunk)
    dest.close()


def get_dir_file_number(path):
    return len(os.listdir(path))


def parse_data_by_path(dest_dir, imei):
    number = get_dir_file_number(dest_dir)

    # enought datasets exist, start converting and training
    if number >= data_source.number2start:
        parse_data(imei, dest_dir)
    return number
