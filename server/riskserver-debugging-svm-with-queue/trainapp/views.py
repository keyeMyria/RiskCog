import json
import os
import subprocess
from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response

# modifyed by Zhengyang for Redis Queue
import django_rq

from arff2libsvm import arff2svmlight
from riskserver import data_source
from riskserver import settings
from trainapp.check import check_is_lie
from trainapp.models import Train
from trainapp.parse import parse_data, create_path
from trainapp.tools import rename_file, testanswer, remove_file, copy_file

queue = django_rq.get_queue('low')
# queue.empty()
import time


# end of modification

def sandeep(request):
    return HttpResponse(json.dumps({'message': 'hello'}), content_type="application/json")


# Create your views here.

class TrainForm(forms.Form):
    imei = forms.CharField()
    path = forms.FileField()


def register(request):
    if request.method == "POST":
        response_dict = {}
        try:
            uf = TrainForm(request.POST, request.FILES)
            if uf.is_valid():

                imei = uf.cleaned_data['imei']
                path = uf.cleaned_data['path']
                ISOTIMEFORMAT = '%Y%m%d%H%M%S'
                name = str(time.strftime(ISOTIMEFORMAT))

                # cp uploaded file to destination_dir/destination_name
                dest_dir = os.path.join(settings.BASE_DIR, "media", "train", imei)
                dest_name = os.path.join(dest_dir, name)
                handle_uploaded_file(path, imei, dest_name)

                # check if the phone is stationary (data to be discarded)
                is_lie = check_is_lie(dest_name)
                if not is_lie:

                    # since this is not a lie, create a training entry in the database
                    train = Train()
                    train.imei = imei
                    train.path = dest_name
                    train.save()

                    # check whether it sits or not
                    create_path(os.path.join(dest_dir, 'data'))
                    copy_file(dest_name, os.path.join(dest_dir, 'data', name))
                    cmd = settings.BASE_DIR + '/bin/check_sit_or_walk.exe' + ' ' + dest_name
                    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    ret_sitwalk = float(p.stdout.readline().split()[1])

                    if ret_sitwalk > 0.6:
                        state = 'walk'
                        create_path(os.path.join(dest_dir, state))
                        rename_file(dest_name, os.path.join(dest_dir, state, name))
                    else:
                        state = 'sit'
                        create_path(os.path.join(dest_dir, state))
                        rename_file(dest_name, os.path.join(dest_dir, state, name))
                    lines = p.communicate()

                else:
                    # since this dataset is a lie, delete it.
                    if os.path.exists(dest_name):
                        os.remove(dest_name)
                    state = 'none'
                    # TODO: shouldn't we return after this?!!!

                print 'the state of the files is ', ret_sitwalk

                # check whether data set is enough to be trained
                number, flodernumber = parse_data_by_path(dest_dir, imei, state, name)

                # check the number of arff file on both sit and walk
                dest_sit_arff_dir = os.path.join(settings.BASE_DIR, "arff", imei, "sit")
                dest_walk_arff_dir = os.path.join(settings.BASE_DIR, "arff", imei, "walk")
                numsitarff = get_dir_file_number(dest_sit_arff_dir)
                numwalkarff = get_dir_file_number(dest_walk_arff_dir)
                # start add code - zyqu
                response_dict["is_lie"] = is_lie
                response_dict["result"] = 0
                response_dict["imei"] = imei
                response_dict["numfiles"] = number
                response_dict["requiredfiles"] = data_source.sumfilesneed
                sitnumber = get_dir_file_number(os.path.join(settings.BASE_DIR, 'media', 'train', imei, 'sit'))
                sitfoldernumber = get_folder_number(os.path.join(settings.BASE_DIR, 'media', 'train', imei, 'sit'))
                walknumber = get_dir_file_number(os.path.join(settings.BASE_DIR, 'media', 'train', imei, 'walk'))
                walkfoldernumber = get_folder_number(os.path.join(settings.BASE_DIR, 'media', 'train', imei, 'walk'))
                response_dict['numsitarff'] = cal_progress_number(sitnumber, sitfoldernumber) + get_dir_file_number(
                    os.path.join(settings.BASE_DIR, 'media', 'train', imei, 'sit', 'Redundant'))
                response_dict['numwalkarff'] = cal_progress_number(walknumber, walkfoldernumber) + get_dir_file_number(
                    os.path.join(settings.BASE_DIR, 'media', 'train', imei, 'walk', 'Redundant'))
                response_dict['state'] = state
                return HttpResponse(json.dumps(response_dict), content_type="application/json")
            # return HttpResponse('upload ok! ' + str(number) +' files. in '+ imei+'.')
            else:
                raise Exception("Transform is not valid")
        except Exception as e:
            response_dict["result"] = -1
            response_dict["message"] = str(e)
            return HttpResponse(json.dumps(response_dict), content_type="application/json")
            # end add code - zyqu

    else:
        uf = TrainForm()

    return render_to_response('register.html', {'uf': uf})


def handle_uploaded_file(f, imei, dest_name):
    tmp_path = os.path.join(settings.BASE_DIR, "media", "train", imei)
    if os.path.isdir(tmp_path):
        pass
    else:
        os.makedirs(tmp_path)

    print '## TRACE ##', 'writing the uploaded path to: ', dest_name
    dest = open(dest_name, "wb+")
    for chunk in f.chunks():
        dest.write(chunk)
    dest.close()


def cal_progress_number(number, foldernumber):
    if foldernumber == 0:
        return number
    elif foldernumber > 0:
        return (foldernumber - 1) * data_source.raw_numebr2start + data_source.number2start
    return 0


def get_dir_file_number(path):
    if not os.path.exists(path):
        return 0

    if not os.path.isdir(path):
        os.system("mkdir %s" % path)

    print '## TRACE ##', 'get number of files that exist at', path
    sum = 0
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            sum += 1
    return sum


def get_folder_number(path):
    if not os.path.exists(path):
        return 0

    if not os.path.isdir(path):
        os.system()

    print '## TRACE ##', 'get number of folders that exist at', path
    sum = 0
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            sum += 1
    return sum


def is_Redundant_or_noise(dest_dir, imei, state, name):
    print '## TRACE ## is_Redundant_or_noise'
    if os.path.exists(os.path.join(settings.BASE_DIR, 'model', imei, state, 'predictor.model')):
        makearff_dir = os.path.join(settings.BASE_DIR, 'bin', 'make_arff.exe')
        dest_path = os.path.join(dest_dir, name)
        cmd = makearff_dir + ' ' + dest_path + ' 1 ' + state
        p = subprocess.Popen(cmd, shell=True, stdout=open(dest_path + '.arff', 'w'))
        p.wait()
        lines = p.communicate()
        arff2svmlight(os.path.join(dest_dir, name + '.arff'), os.path.join(dest_dir, name + '.libsvm'))
        try:
            rec_acc = testanswer(os.path.join(dest_dir, name + '.libsvm'),
                                 os.path.join(settings.BASE_DIR, "model", imei, state, "predictor.model"), imei, state)
            print 'the ACC of', dest_path, rec_acc
            if rec_acc >= data_source.refuse_high_ACC or rec_acc <= data_source.refuse_low_ACC:
                if rec_acc > data_source.refuse_high_ACC:
                    create_path(os.path.join(settings.BASE_DIR, 'media', 'train', imei, state, 'Redundant'))
                    copy_file(dest_path,
                              os.path.join(settings.BASE_DIR, 'media', 'train', imei, state, 'Redundant', name))
                remove_file(os.path.join(dest_dir, name + '.arff'))
                remove_file(os.path.join(dest_dir, name + '.libsvm'))
                remove_file(dest_path)
                return True
        except:
            print 'the ACC of', dest_path, 0.0
            remove_file(os.path.join(dest_dir, name + '.arff'))
            remove_file(os.path.join(dest_dir, name + '.libsvm'))
            remove_file(dest_path)
            return True
        remove_file(os.path.join(dest_dir, name + '.arff'))
        remove_file(os.path.join(dest_dir, name + '.libsvm'))
    return False


def parse_data_by_path(dest_dir, imei, state, name):

    dest_path = os.path.join(dest_dir, state)

    number = get_dir_file_number(dest_path)
    foldernumber = get_folder_number(dest_path)


    # if the file is lie, then return -1
    if state == 'none':
        return number, foldernumber

    # redundant or noisy
    if is_Redundant_or_noise(dest_path, imei, state, name):
        return number, foldernumber

    # ok
    # check if sum of files larger than upper bound
    # if there is more, then delete it
    if cal_progress_number(number, foldernumber) + get_dir_file_number(
            os.path.join(dest_path, 'Redundant')) > data_source.upper_bound_file:
        print "## TRACE ## The " + state + " number have got the upper bound"
        remove_file(os.path.join(dest_path, name))
        return number, foldernumber

    # in the training pulse, data is valid and is no more
    # start converting and training
    # if there are more than 10 files for a specific imei,
    # only then start training else do not train
    if (foldernumber == 0 and number >= data_source.number2start) or (
            foldernumber > 0 and number >= data_source.raw_numebr2start):

        ISOTIMEFORMAT = '%Y%m%d%H%M%S'
        tag = str(time.strftime(ISOTIMEFORMAT))
        orderpath = os.path.join(dest_path, 'data' + tag)
        create_path(orderpath)

        for file in os.listdir(dest_path):
            if os.path.isfile(os.path.join(dest_path, file)):
                rename_file(os.path.join(dest_path, file), os.path.join(orderpath, file))

        # start training
        # add to a queue
        # modifyed by Zhengyang for Redis Queue
        print '***** STARTED TRAINING AT', dest_dir, 'FOR', imei
        # parse_data(imei, dest_dir)
        queue.enqueue(parse_data, imei, orderpath, state, timeout=6000, description=imei)
        # parse_data(imei, dest_dir)
    # end of modification
    return number, foldernumber
