from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation

from comments.models import Comment


class Article(models.Model):
    title = models.CharField('标题', max_length=64)
    body = models.TextField('正文')
    body_html = models.TextField('源码')
    abstract = models.TextField('摘要')
    draft = models.BooleanField('草稿', default=True)
    views = models.PositiveIntegerField('阅读量', default=0)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name='作者'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        verbose_name='分类'
    )
    tags = models.ManyToManyField('Tag', verbose_name='标签集', blank=True)
    topics = models.ManyToManyField('Topic', verbose_name='话题集', blank=True)
    comments = GenericRelation(Comment)

    class Meta:
        ordering = ['-created']
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

class Pin(models.Model):
    body = models.TextField('正文')
    body_html = models.TextField('源码')
    created = models.DateTimeField('创建时间', auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pins',
        verbose_name='作者'
    )
    comments = GenericRelation(Comment)

    class Meta:
        ordering = ['-created']
        verbose_name = '想法'
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


class Category(models.Model):
    name = models.CharField('名称', max_length=32, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父级分类',
        null=True
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Topic(models.Model):
    name = models.CharField('名称', max_length=32, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = '话题'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField('名称', max_length=32, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父级标签',
        null=True
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
