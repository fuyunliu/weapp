import textwrap
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.text import slugify
from markdown import markdown

from commons.managers import GenericManager


class Article(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Draft'
        PUBLISHED = 1, 'Published'

    title = models.CharField('标题', max_length=64)
    body = models.TextField('正文')
    body_html = models.TextField('源码')
    status = models.IntegerField('状态', choices=Status.choices, default=Status.DRAFT)
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)
    updated = models.DateTimeField('更新时间', auto_now=True, editable=False)
    slug = models.SlugField(unique=True, max_length=255)
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
    comments = GenericRelation('comments.Comment')
    likes = GenericRelation('likes.Like')

    objects = GenericManager()

    class Meta:
        ordering = ['-created']
        get_latest_by = 'id'
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.body_html = markdown(self.body, extensions=['fenced_code', 'codehilite'])
        super().save(*args, **kwargs)

    def is_owned(self, user):
        return self.author == user


class Pin(models.Model):
    body = models.TextField('正文')
    body_html = models.TextField('源码')
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pins',
        verbose_name='作者'
    )
    comments = GenericRelation('comments.Comment')
    likes = GenericRelation('likes.Like')

    objects = GenericManager()

    class Meta:
        ordering = ['-created']
        get_latest_by = 'id'
        verbose_name = '想法'
        verbose_name_plural = verbose_name

    def __str__(self):
        return textwrap.shorten(self.body, width=100, placeholder='...')

    def save(self, *args, **kwargs):
        self.body_html = markdown(self.body, extensions=['fenced_code', 'codehilite'])
        super().save(*args, **kwargs)

    def is_owned(self, user):
        return self.author == user


class Category(models.Model):
    name = models.CharField('名称', max_length=32, unique=True)
    desc = models.TextField('描述', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父级分类',
        null=True
    )
    slug = models.SlugField(unique=True, max_length=255)

    objects = GenericManager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Topic(models.Model):
    name = models.CharField('名称', max_length=32, unique=True)
    desc = models.TextField('描述', blank=True)
    slug = models.SlugField(unique=True, max_length=255)

    objects = GenericManager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '话题'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField('名称', max_length=32, unique=True)
    desc = models.TextField('描述', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父级标签',
        null=True
    )
    slug = models.SlugField(unique=True, max_length=255)

    objects = GenericManager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
