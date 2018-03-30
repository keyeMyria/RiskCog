import json
import os
import threading
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response

from riskserver import settings
from testapp.models import Test
from testapp.parse import parse_data
from testapp.probcontroller import *
# modifyed by Zhengyang for Redis Queue
from testapp.profile import *
from testapp.score import get_accuracy, get_recall, get_precision, get_result
from trainapp.check import check_is_lie
from trainapp.tools import get_dir_file_num_contain, remove_file, get_dir_file_number
from trainapp.views import parse_data_by_path

pc = ProbController(0.1)


def create_path(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)


TEST_LOG_DIR = os.path.join(settings.BASE_DIR, "testlogfile", "test")
LOG_DIR = os.path.join(settings.BASE_DIR, "logfile")
create_path(LOG_DIR)


# end of modification


# Create your views here.

class TestForm(forms.Form):
    imei = forms.CharField()
    path = forms.FileField()


# done
def isSit(filePath):
    scriptPath = os.path.join(settings.BASE_DIR, "bin", "check_sit_or_walk.exe")
    cmd = "%s %s" % (scriptPath, filePath)
    print cmd
    output = os.popen(cmd).read()
    val = float(output.split("\t")[1])
    print output, val
    if val > 0.5:
        print "isWalk"
        return False
    else:
        print "isSit"
        return True


# done
# modifyed by Zhengyang for Redis Queue
# rename newThread as test_Task_to_RQ
def test_Task_to_RQ(imei, path, name, dest_dir, dest_name, result_dir, file_cnt):
    profile = Profile(os.path.join(LOG_DIR, "%s_test_Task_to_RQ" % imei))
    # end of modification
    profile.set()
    target_summary_file = os.path.join(result_dir, "summary_%s.txt" % file_cnt)
    remove_file(target_summary_file)
    remove_file(os.path.join(result_dir, "results.txt"))
    profile.log()

    profile.set()
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
    profile.log()

    profile.set()
    # We are writing max of result which is wrong. We should check both walk and sit has to be train above 90%
    # if svm add # to the line below
    # sit_path = os.path.join(settings.BASE_DIR, "model", imei, 'sit', "predictor.vw")
    # if nn add # to the line below
    sit_path = os.path.join(settings.BASE_DIR, "model", imei, 'sit', "predictor.model")
    if os.path.exists(sit_path):
        isSitModelExists = True
        sit_acc, sit_pre, sit_rec = solve_state(result_dir, imei, 'sit', dest_name)
    else:
        isSitModelExists = False
        print "## TRACE ##, Sit model not exist, set all as 0"
        sit_acc, sit_pre, sit_rec = 0.0, 0.0, 0.0

    # if svm add # to the line below
    # walk_path = os.path.join(settings.BASE_DIR, "model", imei, 'walk', "predictor.vw")
    # if nn add # to the line below
    walk_path = os.path.join(settings.BASE_DIR, "model", imei, 'walk', "predictor.model")
    if os.path.exists(walk_path):
        isWalkModelExists = True
        walk_acc, walk_pre, walk_rec = solve_state(result_dir, imei, 'walk', dest_name)
    else:
        isWalkModelExists = False
        print "## TRACE ##, Walk model not exist, set all as 0"
        walk_acc, walk_pre, walk_rec = 0.0, 0.0, 0.0

    # res = max(res1, res2)
    # res = 'sit={},walk={}'.format(res1, res2)
    motionStateisSit = isSit(dest_name)
    res = """sit_accuracy={},walk_accuracy={}
sit_precision={},walk_precision={}
sit_recall={},walk_recall={},isSitModelExists={},isWalkModelExists={},isSit={}"""\
        .format(sit_acc, walk_acc, sit_pre,
                walk_pre, sit_rec, walk_rec,
                isSitModelExists,
                isWalkModelExists,
                motionStateisSit)

    print '## TRACE ##', 'writing summary to', target_summary_file
    if not os.path.exists(result_dir):
        create_path(result_dir)
    fp = open(target_summary_file, "w")
    fp.write(str(res))
    fp.close()
    profile.log()
    # modifyed by Zhengyang: execute training task with probility
    # if pc.isHit() and (float(sit_acc) > 0.85 or float(walk_acc) > 0.85):
    if False:
        # add test file to train
        target_train_dir = os.path.join(settings.BASE_DIR, "media", "train", imei)
        target_train_file = os.path.join(target_train_dir, name)
        if not os.path.exists(target_train_dir):
            os.makedirs(target_train_dir)
        if not os.path.exists(target_train_file) or (
                    os.path.exists(target_train_file) and os.path.getsize(target_train_file) != os.path.getsize(
                    dest_name)):
            print '## TRACE ##', 'copying ', dest_name, 'to', target_train_file
            open(target_train_file, "wb").write(open(dest_name, "rb").read())

        number = parse_data_by_path(target_train_dir, imei)
        # print("sit  result  = " + str(res1))
        # print("walk result  = " + str(res2))
    print res
    return res
    # return HttpResponse('upload ok! ' + str(number) +' files. in '+ imei+'.')
    # return_res = {'max_version': file_cnt}
    # return HttpResponse(json.dumps(return_res), content_type="application/json")


# done
# check the row data, store it and start an parsing thread
def register(request):
    if request.method == "POST":
        uf = TestForm(request.POST, request.FILES)
        if uf.is_valid():
            try:
                imei = uf.cleaned_data['imei']
                path = uf.cleaned_data['path']

                ISOTIMEFORMAT = '%Y%m%d%H%M%S'
                name = str(time.strftime(ISOTIMEFORMAT))
                dest_dir = os.path.join(settings.BASE_DIR, "media", "test", imei)
                dest_name = os.path.join(dest_dir, name)
                handle_uploaded_file(path, imei, dest_name)

                # prepare for creating a new summary file
                result_dir = os.path.join(settings.BASE_DIR, "result", imei)
                file_cnt = get_dir_file_num_contain(result_dir, "summary")
                return_res = {'max_version': file_cnt}
                return HttpResponse(json.dumps(return_res), content_type="application/json")
            except Exception as e:
                print str(e)
                return_res = {'max_version': '-1'}
                return HttpResponse(json.dumps(return_res), content_type="application/json")
            finally:
                # modifyed by Zhengyang for Redis Queue
                # django_rq.enqueue(test_Task_to_RQ, imei, path, name, dest_dir, dest_name, result_dir, file_cnt)
                t = threading.Thread(target=test_Task_to_RQ,
                                     args=(imei, path, name, dest_dir, dest_name, result_dir, file_cnt,), kwargs={})
                t.setDaemon(True)
                t.start()
                # end of modification


    else:
        uf = TestForm()

    return render_to_response('register.html', {'uf': uf})


def solve_state(result_dir, imei, state, dest_name):
    # modified by Zhengyang for profiling
    profile = Profile(os.path.join(LOG_DIR, "%s_solve_state" % imei))
    # end of modification
    profile.set()
    create_path(result_dir)
    # if svm add # before the line below
    # vw_path = os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.vw")
    # if nn add # before the line below
    vw_path = os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.model")
    data_set = parse_data(imei, dest_name)
    ISOTIMEFORMAT = '%Y%m%d%H%M%S'
    time_stamp = str(time.strftime(ISOTIMEFORMAT))
    result_path = os.path.join(result_dir, "results.txt_%s_%s" % (state, time_stamp))
    profile.log()

    profile.set()
    if not os.path.exists(vw_path):
        return 0.0, 0.0, 0.0

    if count_lines(data_set) < 10:  # 1000:
        # This data set is has very less number of data points. do not process.
        raise Exception('Very less data points to train')

    # perform random sampling and cross validation here.
    # regenerate a fresh dataset here to check the accuracy.

    # if state == 'sit':
    #     dest_arff_dir = os.path.join(settings.BASE_DIR, "arff", imei, "sit")
    # else:
    #     dest_arff_dir = os.path.join(settings.BASE_DIR, "arff", imei, "walk")
    # numarff = get_dir_file_number(dest_arff_dir)
    # print '## TRACE ##', 'get file number for', state, ':', numarff

    # test profile
    # when use svm, add # on the line below
    # profile1 = Profile(os.path.join(TEST_LOG_DIR, "%s_nn_%s_%s" % (imei, numarff, state)))
    # when use nn, add # on the line below
    # profile1 = Profile(os.path.join(TEST_LOG_DIR, "%s_svm_%s_%s" % (imei, numarff, state)))
    # profile1.set()

    # if svm add # below
    # cmd = "vw -d " + data_set + " -t -i " + vw_path + " -p " + result_path
    # if nn add # below
    cmd  = "bin/svm-predict -b 1 " + data_set + " " + vw_path + " " + result_path
    print '## TRACE ##', 'training', cmd

    output = os.popen(cmd)
    # profile1.log()
    print(output.read())

    profile.set()
    print "## TRACE ## datasetPath: %s, resultPath %s" % (data_set, result_path)
    # if svm add # before the three lines below
    # res_acc = get_accuracy(data_set, result_path)
    # res_pre = get_precision(data_set, result_path)
    # res_rec = get_recall(data_set, result_path)
    # if nn add # below
    remove_file(data_set)
    res_acc, res_pre, res_rec = get_result(result_path)
    profile.log()
    #			remove_file(result_path)
    return res_acc, res_pre, res_rec


# done
# store the raw data
def handle_uploaded_file(f, imei, dest_name):
    tmp_path = os.path.join(settings.BASE_DIR, "media", "test", imei)
    if os.path.isdir(tmp_path):
        pass
    else:
        os.makedirs(tmp_path)

    print '## TRACE ##', 'writing the uploaded path to: ', dest_name
    dest = open(dest_name, "wb+")
    for chunk in f.chunks():
        dest.write(chunk)
    dest.close()


def count_lines(path):
    counter = 0
    for line in open(path, 'r'):
        counter += 1

    return counter
