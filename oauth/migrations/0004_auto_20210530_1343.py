# Generated by Django 3.2 on 2021-05-30 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0003_alter_user_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.PositiveSmallIntegerField(choices=[(None, '保密'), (0, '男'), (1, '女')], null=True, verbose_name='性别'),
        ),
        migrations.AlterField(
            model_name='region',
            name='level',
            field=models.PositiveSmallIntegerField(choices=[(1, '省'), (2, '市'), (3, '县'), (4, '镇'), (5, '村')], verbose_name='级别'),
        ),
    ]