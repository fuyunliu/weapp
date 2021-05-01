from django.conf import settings
from django.core.mail import get_connection
from celery import shared_task


@shared_task(serializer='pickle')
def send_email(messages, backend_kwargs=None, **kwargs):
    kwds = backend_kwargs or {}
    kwds.update(kwargs)

    with get_connection(backend=settings.CELERY_EMAIL_BACKEND, **kwds) as conn:
        num_sent = conn.send_messages(messages)

    return num_sent


@shared_task
def send_digits(digits):
    print(f'Send phone digits: {digits}')
