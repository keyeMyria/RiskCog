import json
import os
import subprocess
import time
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response

# modifyed by Zhengyang for Redis Queue
import django_rq

from riskserver import settings
from testapp.views import solve_state
from trainapp.tools import get_dir_file_num_contain, remove_file
from trainapp.views import parse_data_by_path

queue = django_rq.get_queue('low')


# end of modification

# Create your views here.

class QueryForm(forms.Form):
    imei = forms.CharField()
    version = forms.CharField()


# modifyed by Zhengyang for Redis Queue
# rename newThread as manual_fix_Task_to_RQ
def manual_fix_Task_to_RQ(imei, path, name, dest_dir, dest_name, result_dir, file_cnt):
    # end of modification
    target_summary_file = os.path.join(result_dir, "summary_%s.txt" % file_cnt)
    remove_file(target_summary_file)
    remove_file(os.path.join(result_dir, "results.txt"))

    # NO NEED TO CHECK FOR LIE SINCE THIS IS RE-TRAINING ON MANUAL FIX
    # is_lie = check_is_lie(dest_name)
    # if not is_lie:
    #     test = Test()
    #     test.imei = imei
    #     test.path = dest_name
    #     test.save()
    # else:
    #     # here need return a JSON lie
    #     if os.path.exists(dest_name):
    #         os.remove(dest_name)
    target_train_dir = os.path.join(settings.BASE_DIR, "media", "train", imei)
    # os.path.join(settings.BASE_DIR, "media", "train", imei)
    number = parse_data_by_path(target_train_dir, imei)

    # We are writing max of result which is wrong. We should check both walk and sit has to be train above 90%
    sit_acc, sit_pre, sit_rec = solve_state(result_dir, imei, 'sit', dest_name)
    walk_acc, walk_pre, walk_rec = solve_state(result_dir, imei, 'walk', dest_name)
    # res = max(res1, res2)
    # res = 'sit={},walk={}'.format(res1, res2)

    res = """sit_accuracy={},walk_accuracy={}
sit_precision={},walk_precision={}
sit_recall={},walk_recall={}""".format(sit_acc, walk_acc, sit_pre, walk_pre, sit_rec, walk_rec)

    fp = open(target_summary_file, "w")
    fp.write(str(res))
    fp.close()

    # # add test file to train
    # target_train_dir = os.path.join(settings.BASE_DIR, "media", "train", imei)
    # target_train_file = os.path.join(target_train_dir, name)
    # if not os.path.exists(target_train_dir):
    #     os.makedirs(target_train_dir)
    # if not os.path.exists(target_train_file) or (
    #             os.path.exists(target_train_file) and os.path.getsize(target_train_file) != os.path.getsize(
    #             dest_name)):
    #     open(target_train_file, "wb").write(open(dest_name, "rb").read())
    # print("sit  result  = " + str(res1))
    # print("walk result  = " + str(res2))
    print res


# return HttpResponse('upload ok! ' + str(number) +' files. in '+ imei+'.')
# return_res = {'max_version': file_cnt}
# return HttpResponse(json.dumps(return_res), content_type="application/json")


def query(request):
    if request.method == 'POST':
        uf = QueryForm(request.POST, request.FILES)
        if uf.is_valid():
            imei = uf.cleaned_data['imei']
            version = uf.cleaned_data['version']
            result_dir = os.path.join(settings.BASE_DIR, "result", imei)
            file_cnt = get_dir_file_num_contain(result_dir, "summary")

            # todo : use file_cnt to judge invalid situations (too large version number)
            target_file = os.path.join(result_dir, "summary_%s.txt" % version)
            return_res = {}
            if os.path.exists(target_file):
                f = open(target_file)
                return_res['result'] = f.read()
                return_res['version'] = version
            return HttpResponse(json.dumps(return_res), content_type="application/json")

    else:
        uf = QueryForm()

    return render_to_response('register.html', {'uf': uf})


class FixForm(forms.Form):
    imei = forms.CharField()
    version = forms.IntegerField()
    signal = forms.IntegerField()


def manual_fix(request):
    if request.method == 'POST':
        uf = FixForm(request.POST, request.FILES)
        if uf.is_valid():
            imei = uf.cleaned_data['imei']
            version = uf.cleaned_data['version']
            signal = uf.cleaned_data['signal']
            if signal > 1 | signal < 0:
                return HttpResponse("invalid signal")
            ISOTIMEFORMAT = '%Y%m%d%H%M%S'
            name = str(time.strftime(ISOTIMEFORMAT))
            dest_dir = os.path.join(settings.BASE_DIR, "media", "test", imei)
            dest_name = get_nth_filename(dest_dir, version)
            if dest_name is None:
                raise Exception("There is no " + str(version) + "th file!")

            # invoke manualFix.py
            train_dir = os.path.join(settings.BASE_DIR, "media", "train", imei)
            manualFixPath = os.path.join(settings.BASE_DIR, "query", "manualFix.py")
            file_names = []
            for dirpath, dirs, files in os.walk(train_dir):
                for filepath in files:
                    VWSourceFilePath = os.path.join(dirpath, filepath)
                    CorrectSamplePath = dest_name
                    OutputFilePath = VWSourceFilePath

                    cmd = 'python ' + manualFixPath + ' ' + VWSourceFilePath + ' ' + CorrectSamplePath + ' ' + \
                          str(signal) + ' 2.0 ' + OutputFilePath
                    print(cmd)
                    file_names.append(cmd.rsplit('/', 1)[-1])
                    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    p.wait()

            # train the model on the fixed training data
            parse_data_by_path(train_dir, imei)

            # compute the summary before returning

            ISOTIMEFORMAT = '%Y%m%d%H%M%S'
            name = str(time.strftime(ISOTIMEFORMAT))
            dest_dir = os.path.join(settings.BASE_DIR, "media", "test", imei)
            dest_name = os.path.join(dest_dir, name)
            result_dir = os.path.join(settings.BASE_DIR, "result", imei)
            file_cnt = get_dir_file_num_contain(result_dir, "summary")
            # modifyed by Zhengyang for Redis Queue
            queue.enqueue(manual_fix_Task_to_RQ, imei, None, name, dest_dir, dest_name, result_dir, file_cnt,
                          timeout=6000)
            # t = threading.Thread(
            #    target=manual_fix_Task_to_RQ, 
            #    args=(imei, None, name, dest_dir, dest_name, result_dir, file_cnt, ), 
            #    kwargs={}
            # )
            # t.setDaemon(True)
            # t.start()

            # end of modification
            # EXAMPLES:
            # python /space/srp243/riskserver-debugging-20161025/query/manualFix.py /space/srp243/riskserver-debugging-20161025/media/train/asdsada324934893434/20161109003230 /space/srp243/riskserver-debugging-20161025/media/test/asdsada324934893434/20161109003655 0 2.0 /space/srp243/riskserver-debugging-20161025/media/train/asdsada324934893434/20161109003230

            # /space/srp243/riskserver-debugging-20161025/media/train/ashdhsa12121212

            result = {"imei": imei, "received_signal": signal}
            result['isValid'] = True
            return HttpResponse(json.dumps(result), content_type="application/json")
        else:
            raise Exception("Form is not valid")
    else:
        uf = FixForm()

    return render_to_response('register.html', {'uf': uf})


def get_nth_filename(dir_path, n):
    cnt = 0
    for dirpath, dirs, files in os.walk(dir_path):
        for filepath in files:
            if cnt == n:
                return os.path.join(dir_path, filepath)
            else:
                cnt += 1
    return None
