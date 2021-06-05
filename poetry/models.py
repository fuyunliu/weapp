import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('名字', max_length=64)
    dynasty = models.CharField('朝代', max_length=64)
    desc = models.TextField('描述', blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '作者'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class TangPoem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200))

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '唐诗'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class SongPoem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '宋诗'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class SongLyric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.CharField('作者', max_length=64)
    rhythm = models.CharField('韵律', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '宋词'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.rhythm


class CaoCao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '曹操'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ChuLyric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    section = models.CharField('章节', max_length=64)
    content = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '楚辞'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class LunYu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '论语'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Shijing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    chapter = models.CharField('篇章', max_length=64)
    section = models.CharField('章节', max_length=64)
    content = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '诗经'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class YuanQu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    dynasty = models.CharField('朝代', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '元曲'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class HuaJianji(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    rhythm = models.CharField('韵律', max_length=64)
    notes = ArrayField(models.CharField(max_length=200), blank=True)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '花间集'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class NanTang(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    rhythm = models.CharField('韵律', max_length=64)
    notes = ArrayField(models.CharField(max_length=200), blank=True)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '南唐'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Strain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strains = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '诗词平仄'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id


class BaiJiaXing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    dynasty = models.CharField('朝代', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '百家姓'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class XingOrigin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    dynasty = models.CharField('朝代', max_length=64)
    surname = models.CharField('姓氏', max_length=64)
    place = models.CharField('位置', max_length=64)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '百家姓起源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class DiZiGui(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    chapter = models.CharField('篇章', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '弟子规'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class GuWenGuanZhi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    source = models.CharField('来源', max_length=64)
    chapter = models.CharField('篇章', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '古文观止'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class QianJiaShi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    tape = models.CharField('类型', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '千家诗'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class QianZiWen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    dynasty = models.CharField('朝代', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '千字文'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class SanZiJing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    tape = models.CharField('类型', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '三字经'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ShiSanBai(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    tape = models.CharField('类型', max_length=64)
    chapter = models.CharField('篇章', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '唐诗三百首'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ZhiZiJiaXun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    author = models.CharField('作者', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '朱子家训'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class SiShuWuJing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('标题', max_length=64)
    paragraphs = ArrayField(models.CharField(max_length=200), blank=True)

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '四书五经'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
