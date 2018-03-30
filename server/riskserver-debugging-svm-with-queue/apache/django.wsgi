import os

import sys


path = '/home/zyshao/riskserver'
if path not in sys.path:
    sys.path.insert(0, '/home/zyshao/riskserver')
os.environ['DJANGO_SETTINGS_MODULE'] = 'riskserver.settings'
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

