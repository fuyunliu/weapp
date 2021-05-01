import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weapp.settings')

app = Celery('weapp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(packages=['commons.mail'])
app.autodiscover_tasks()
