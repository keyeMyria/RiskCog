# use normal python, please run
# python manage.py shell < queue_clearing

from time import sleep
from operator import itemgetter
import django_rq

# cycle time
TIMEOUT = 5

while True:
    queue_id = None
    imei = None
    model_box = None
    file_number = None

    queue = django_rq.get_queue('trainer')
    print 'get queue trainer'

    jobs = queue.get_jobs()
    print 'we have {0} jobs'.format(len(jobs))

    # sort by imei, model_box
    jobs = sorted(jobs, key=lambda job: job.args[0].imei + str(job.args[2]))

    for job in jobs:
        current_imei = job.args[0]
        current_model_box = job.args[2]
        current_file_number = len(job.args[1])
        current_queue_id = job.id
        print '## current is', current_imei, current_model_box, current_file_number

        if (current_imei, current_model_box) == (imei, model_box):
            if current_file_number >= file_number:
                # delete the last one
                ret = queue.remove(queue_id)
                print '## remove job', queue_id, imei, model_box, file_number
                imei = current_imei
                model_box = current_model_box
                file_number = current_file_number
                queue_id = current_queue_id
        else:
            imei = current_imei
            model_box = current_model_box
            file_number = current_file_number
            queue_id = current_queue_id
    sleep(TIMEOUT)
