import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weblog.settings')

app = Celery('weblog')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(packages=['commons.mail'])
app.autodiscover_tasks()
