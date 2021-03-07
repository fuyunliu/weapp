from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify


class Article(models.Model):
    title = models.CharField('标题', max_length=64, db_index=True)
    body = models.TextField('正文')
    body_html = models.TextField('源码')
    abstract = models.TextField('摘要')
    draft = models.BooleanField('草稿', default=True)
    created = models.DateTimeField('创建时间', default=timezone.now)
    updated = models.DateTimeField('更新时间', default=timezone.now)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='作者',
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='分类',
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField('Tag', verbose_name='标签集合', blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField('分类名', max_length=30, db_index=True)
    parent = models.ForeignKey(
        'self',
        verbose_name='父级分类',
        on_delete=models.CASCADE
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('标签名', max_length=30, db_index=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
