import textwrap

from django.db import models
from django.conf import settings
from commons.managers import GenericQuerySet


class Question(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='发布者'
    )
    title = models.CharField('标题', max_length=64)
    max_choices = models.IntegerField('最多几项')
    created = models.DateTimeField('创建时间', auto_now_add=True, editable=False)

    objects = GenericQuerySet.as_manager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '问题'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def is_owned(self, user):
        return self.owner == user


class Choice(models.Model):
    title = models.CharField('标题', max_length=64)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='问题'
    )

    objects = GenericQuerySet.as_manager()

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def is_owned(self, user):
        return self.question.owner == user


class Vote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='用户'
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='选项'
    )

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
        verbose_name = '投票'
        verbose_name_plural = verbose_name
        unique_together = [['user', 'choice']]

    def __str__(self):
        choice_title = textwrap.shorten(self.choice.title, width=10, placeholder='...')
        return f'{self.user.username} - {choice_title}'

    def is_owned(self, user):
        return self.user == user
