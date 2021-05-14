from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class LikeManager(models.Manager):

    def is_liked(self, obj, user):
        if not user.is_authenticated:
            return False

        return self.filter(sender=user, content_type=ContentType.objects.get_for_model(obj), object_id=obj.pk).exists()


class Like(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='发起者'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='内容类型')
    object_id = models.PositiveIntegerField(verbose_name='对象主键')
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)

    objects = LikeManager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '喜欢'
        verbose_name_plural = verbose_name
        unique_together = [['sender', 'content_type', 'object_id']]

    def __str__(self):
        return f'{self.sender} -> {self.content_object}'
