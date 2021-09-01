import textwrap

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.expressions import F
from django.utils.text import slugify
from markdown import markdown

from commons.managers import GenericQuerySet, ManagerDescriptor, GenericReversedManager


class Article(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Draft'
        PUBLISHED = 1, 'Published'

    title = models.CharField('标题', max_length=64)
    body = models.TextField('正文')
    body_html = models.TextField('源码', editable=False)
    status = models.PositiveSmallIntegerField('状态', choices=Status.choices, default=Status.DRAFT, editable=False)
    view_count = models.PositiveIntegerField('浏览量', default=0, editable=False)
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)
    updated = models.DateTimeField('更新时间', auto_now=True, editable=False)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
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
    topics = models.ManyToManyField('Topic', verbose_name='话题集', blank=True)
    likes = GenericRelation('likes.Like')
    comments = GenericRelation('comments.Comment')
    collects = GenericRelation('collects.Collect')

    # 文章的标签
    tags = ManagerDescriptor(manager=GenericReversedManager, through='taggit.TaggedItem', target='taggit.Tag')

    # 喜欢文章的人
    likers = ManagerDescriptor(manager=GenericReversedManager, through='likes.Like', target='oauth.User')

    # 收藏文章的收藏夹
    collections = ManagerDescriptor(manager=GenericReversedManager, through='collects.Collect', target='collects.Collection')

    objects = GenericQuerySet.as_manager()

    class Meta:
        ordering = ['-created']
        get_latest_by = 'id'
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = self._unique_slug()
        self.body_html = markdown(self.body, extensions=['fenced_code', 'codehilite'])
        super().save(*args, **kwargs)

    @property
    def excerpt(self):
        return self.shorten(width=200)

    @property
    def content_type(self):
        ct = ContentType.objects.get_for_model(self)
        return f'{ct.app_label}.{ct.model}'

    def shorten(self, width):
        return textwrap.shorten(self.body, width=width, placeholder='...')

    def viewed(self):
        self.view_count = F('view_count') + 1
        self.save(update_fields=['view_count'])
        self.refresh_from_db()

    def is_owned(self, user):
        return self.author == user

    def _unique_slug(self):
        # 如果原标题不存在，则直接使用原标题
        origin_unique_slug = slugify(self.title, allow_unicode=True)
        if not self.__class__.objects.filter(slug=origin_unique_slug).exists():
            return origin_unique_slug

        # 如果原标题存在，则在原标题结尾加数字
        num = 1
        unique_slug = f'{origin_unique_slug}-{num}'
        while self.__class__.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{origin_unique_slug}-{num}'
            num += 1
        return unique_slug


class Post(models.Model):
    body = models.TextField('正文')
    body_html = models.TextField('源码', editable=False)
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='作者'
    )
    likes = GenericRelation('likes.Like')
    comments = GenericRelation('comments.Comment')
    collects = GenericRelation('collects.Collect')

    # 喜欢动态的人
    likers = ManagerDescriptor(manager=GenericReversedManager, through='likes.Like', target='oauth.User')

    # 收藏想法的收藏夹
    collections = ManagerDescriptor(manager=GenericReversedManager, through='collects.Collect', target='collects.Collection')

    objects = GenericQuerySet.as_manager()

    class Meta:
        ordering = ['-id']
        get_latest_by = 'id'
        verbose_name = '动态'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.shorten(width=10)

    def save(self, *args, **kwargs):
        self.body_html = markdown(self.body, extensions=['fenced_code', 'codehilite'])
        super().save(*args, **kwargs)

    @property
    def excerpt(self):
        return self.shorten(width=200)

    @property
    def content_type(self):
        ct = ContentType.objects.get_for_model(self)
        return f'{ct.app_label}.{ct.model}'

    def shorten(self, width):
        return textwrap.shorten(self.body, width=width, placeholder='...')

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
    slug = models.SlugField(max_length=255, unique=True, editable=False)

    # 关注分类的人
    followers = ManagerDescriptor(manager=GenericReversedManager, through='follows.Follow', target='oauth.User')

    objects = GenericQuerySet.as_manager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Topic(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name='创建者'
    )
    name = models.CharField('名称', max_length=32, unique=True)
    desc = models.TextField('描述', blank=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)

    # 关注话题的人
    followers = ManagerDescriptor(manager=GenericReversedManager, through='follows.Follow', target='oauth.User')

    objects = GenericQuerySet.as_manager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '话题'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def is_owned(self, user):
        return self.creator == user
