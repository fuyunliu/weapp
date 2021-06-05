import textwrap
from django.db import models
from django.conf import settings

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class Message(models.Model):
    body = models.TextField('消息')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='发送者',
        db_index=True
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recieved_messages',
        verbose_name='接收者',
        db_index=True
    )
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False, db_index=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '消息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return textwrap.shorten(self.body, width=10, placeholder='...')

    def save(self, *args, **kwargs):
        new = self.id
        self.body = self.body.strip()
        super().save(*args, **kwargs)
        if new is None:
            self.notify_clients()

    def is_owned(self, user):
        return self.sender == user

    def notify_clients(self):
        msg = {
            'type': 'recieve_group_message',
            'message': f'{self.id}'
        }

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(f'{self.sender.pk}', msg)
        async_to_sync(channel_layer.group_send)(f'{self.receiver.pk}', msg)
