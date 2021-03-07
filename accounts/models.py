from django.db import models
from django.contrib.auth.models import AbstractUser


class FireUser(AbstractUser):
    nickname = models.CharField('昵称', max_length=64, blank=True)
    location = models.CharField('位置', max_length=64, blank=True)
    about_me = models.TextField('简介', blank=True)
    avatar_hash = models.CharField('头像哈希值', max_length=32)

    class Meta:
        ordering = ['-id']
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def __str__(self):
        return f'<FireUser {self.username}>'
