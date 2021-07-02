from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Tag(models.Model):
    name = models.CharField('名称', unique=True, max_length=32)
    slug = models.SlugField(unique=True, max_length=255, editable=False)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class TaggedItem(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='标签'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='内容类型')
    object_id = models.PositiveIntegerField(verbose_name='对象主键', db_index=True)
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '标签项'
        verbose_name_plural = verbose_name
        index_together = [['content_type', 'object_id']]
        unique_together = [['content_type', 'object_id', 'tag']]

    def __str__(self):
        return f'{self.tag} -> {self.content_object}'

    def is_owned(self, user):
        try:
            return self.content_object.is_owned(user)
        except AttributeError:
            return False
