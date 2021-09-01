from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from markdown import markdown

from commons.managers import ManagerDescriptor, GenericReversedManager


def get_sentinel_user():
    user, _ = get_user_model().objects.get_or_create(username='deleted')
    return user


class Comment(models.Model):
    body = models.TextField('正文')
    body_html = models.TextField('源码')
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
        related_name='comments',
        verbose_name='作者'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='父级评论',
        null=True
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='内容类型')
    object_id = models.PositiveIntegerField(verbose_name='对象主键', db_index=True)
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    enabled = models.BooleanField('是否显示', default=True)

    # 喜欢评论的人
    likers = ManagerDescriptor(manager=GenericReversedManager, through='likes.Like', target='oauth.User')

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.author} -> {self.content_object}'

    def save(self, *args, **kwargs):
        self.body_html = markdown(self.body, extensions=['fenced_code', 'codehilite'])
        super().save(*args, **kwargs)

    def is_owned(self, user):
        return self.author == user
