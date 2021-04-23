from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Like(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='发起者'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)

    class Meta:
        ordering = ['id']
        unique_together = [['sender', 'content_type', 'object_id']]
        verbose_name = '点赞'
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def __str__(self):
        return f"{self.sender} -> {self.content_object}"
