import django_rq

queue_tester = django_rq.get_queue('tester')