import json
import os
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response

from riskserver import settings
from trainapp.tools import get_dir_file_number


# Create your views here.

class QueryForm(forms.Form):
    imei = forms.CharField()
    version = forms.CharField()


def query(request):
    if request.method == 'POST':
        uf = QueryForm(request.POST, request.FILES)
        if uf.is_valid():
            imei = uf.cleaned_data['imei']
            version = uf.cleaned_data['version']
            result_dir = os.path.join(settings.BASE_DIR, "result", imei)
            file_cnt = get_dir_file_number(result_dir) / 2
            target_file = os.path.join(result_dir, "summary_" + version + ".txt")
            return_res = {}
            if os.path.exists(target_file):
                f = open(target_file)
                return_res['result'] = float(f.read())
                return_res['version'] = version
            return HttpResponse(json.dumps(return_res), content_type="application/json")

    else:
        uf = QueryForm()

    return render_to_response('register.html', {'uf': uf})
