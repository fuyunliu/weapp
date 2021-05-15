from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from commons.managers import GenericManager


class Collection(models.Model):
    name = models.CharField('名称', max_length=32)
    desc = models.TextField('描述', blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='用户'
    )

    objects = GenericManager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '收藏夹'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def is_owned(self, user):
        return self.user == user


class CollectManager(models.Manager):

    def is_collected(self, user, obj):
        if not user.is_authenticated:
            return False

        return self.filter(sender=user, content_type=ContentType.objects.get_for_model(obj), object_id=obj.pk).exists()


class Collect(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='collects',
        verbose_name='收藏夹'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='内容类型')
    object_id = models.PositiveIntegerField(verbose_name='对象主键')
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)

    objects = CollectManager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '收藏'
        verbose_name_plural = verbose_name
        unique_together = [['collection', 'content_type', 'object_id']]

    def __str__(self):
        return f'{self.collection} -> {self.content_object}'

    def is_owned(self, user):
        return self.collection.user == user
