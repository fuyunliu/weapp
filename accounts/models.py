from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # stars=我关注的人 fans=关注我的人
    stars = models.ManyToManyField(
        'self',
        related_name='fans',
        symmetrical=False, # 非对称关系
        verbose_name='我关注的人'
    )


class Profile(models.Model):
    class Gender(models.IntegerChoices):
        MALE = 0, 'Male'
        FEMALE = 1, 'Female'

        __empty__ = 'Unknown'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )
    nickname = models.CharField('昵称', max_length=64, unique=True)
    gender = models.IntegerField('性别', choices=Gender.choices)
    location = models.CharField('地区', max_length=64, blank=True)
    about_me = models.TextField('个性签名', blank=True)
    avatar_hash = models.CharField('头像哈希值', max_length=32)

    class Meta:
        ordering = ['-user_id']
        verbose_name = '个人资料'
        verbose_name_plural = verbose_name
        get_latest_by = 'user_id'

    def __str__(self):
        return f'<Profile {self.nickname}>'


class Region(models.Model):
    class Level(models.IntegerChoices):
        PROVINCCE = 1, 'Province'
        CITY = 2, 'City'
        COUNTRY = 3, 'Country'
        TOWN = 4, 'Town'
        VILLAGE = 5, 'Village'

    name = models.CharField('名称', max_length=32)
    code = models.CharField('代码', max_length=32)
    level = models.IntegerField('级别', choices=Level.choices)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='上级地区',
        null=True
    )

    class Meta:
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name
