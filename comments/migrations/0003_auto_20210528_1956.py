# Generated by Django 3.2 on 2021-05-28 11:56

import comments.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comments', '0002_auto_20210523_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=models.SET(comments.models.get_sentinel_user), related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='作者'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=models.SET_NULL, related_name='children', to='comments.comment', verbose_name='父级评论'),
        ),
    ]
