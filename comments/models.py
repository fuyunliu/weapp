from django.db import models
from django.conf import settings
from django.utils import timezone
from blog.models import Article


class Comment(models.Model):
    body = models.TextField('正文')
    body_html = models.TextField('源码')
    created = models.DateTimeField('创建时间', default=timezone.now)
    updated = models.DateTimeField('更新时间', default=timezone.now)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='作者',
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Article,
        verbose_name='文章',
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'self',
        verbose_name='父级评论',
        on_delete=models.CASCADE
    )
    enable = models.BooleanField('是否显示', default=True)

    class Meta:
        ordering = ['id']
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
