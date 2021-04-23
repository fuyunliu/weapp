from django.db import models
from django.conf import settings


class Message(models.Model):
    body = models.TextField('消息')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='from_user',
        verbose_name='发送者',
        db_index=True
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='to_user',
        verbose_name='接收者',
        db_index=True
    )
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False, db_index=True)
