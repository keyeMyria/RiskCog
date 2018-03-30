# when use normal python, please run
# python manage.py shell < queue_clearing.py
# when use ipython, please run
# python manage.py shell < queue_clearing
from time import sleep
import django_rq

# cycle time
TIMEOUT = 5

while True:
    current_imei = None
    index = 0
    queue = django_rq.get_queue('low')
    print '\n## get queues', queue
    jobs = queue.get_jobs()
    print '## get jobs', jobs
    for job in jobs:
        current_imei = job.description
        print '## current imei', current_imei
#        if job.description == current_imei:
#            if index == 0:
#                ret = queue.remove(job.id)
#                print '## remove job', job, ret
#        else:
#            current_imei = job.description
#            print '## current imei', current_imei
#            index = 0
    sleep(TIMEOUT)
