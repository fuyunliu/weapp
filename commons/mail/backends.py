from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

from commons.mail.tasks import send_email
from commons.utils import chunks


class CeleryEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently)
        self.back_kwargs = kwargs

    def send_messages(self, email_messages):
        results = []
        for chunk in chunks(email_messages, settings.CELERY_EMAIL_CHUNK_SIZE):
            results.append(send_email.delay(chunk), self.back_kwargs)
        return results
