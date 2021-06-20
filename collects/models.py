from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from commons.managers import GenericQuerySet, ManagerDescriptor, GenericRelatedManager, GenericReversedManager


class Collection(models.Model):
    name = models.CharField('名称', max_length=32)
    desc = models.TextField('描述', blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='所有者'
    )

    objects = GenericQuerySet.as_manager()

    # 收藏夹收藏的文章
    articles = ManagerDescriptor(manager=GenericRelatedManager, through='collects.Collect', target='weblog.Article')

    # 收藏夹收藏的想法
    pins = ManagerDescriptor(manager=GenericRelatedManager, through='collects.Collect', target='weblog.Pin')

    # 喜欢收藏夹的人
    likers = ManagerDescriptor(manager=GenericReversedManager, through='likes.Like', target='oauth.User')

    # 关注收藏夹的人
    followers = ManagerDescriptor(manager=GenericReversedManager, through='follows.Follow', target='oauth.User')

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '收藏夹'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def is_owned(self, user):
        return self.owner == user


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
    object_id = models.PositiveIntegerField(verbose_name='对象主键', db_index=True)
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)

    objects = CollectManager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '收藏'
        verbose_name_plural = verbose_name
        index_together = [['content_type', 'object_id']]
        unique_together = [['content_type', 'object_id', 'collection']]

    def __str__(self):
        return f'{self.collection} -> {self.content_object}'

    def is_owned(self, user):
        return self.collection.owner == user
