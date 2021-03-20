# Generated by Django 3.1.7 on 2021-03-14 09:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='名称')),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name': '话题',
                'verbose_name_plural': '话题',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='名称')),
                ('slug', models.SlugField(unique=True)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='blog.tag', verbose_name='父级标签')),
            ],
            options={
                'verbose_name': '标签',
                'verbose_name_plural': '标签',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Pin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(verbose_name='正文')),
                ('body_html', models.TextField(verbose_name='源码')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pins', to=settings.AUTH_USER_MODEL, verbose_name='作者')),
            ],
            options={
                'verbose_name': '想法',
                'verbose_name_plural': '想法',
                'ordering': ['-created'],
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='名称')),
                ('slug', models.SlugField(unique=True)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='blog.category', verbose_name='父级分类')),
            ],
            options={
                'verbose_name': '分类',
                'verbose_name_plural': '分类',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=64, verbose_name='标题')),
                ('body', models.TextField(verbose_name='正文')),
                ('body_html', models.TextField(verbose_name='源码')),
                ('abstract', models.TextField(verbose_name='摘要')),
                ('draft', models.BooleanField(default=True, verbose_name='草稿')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='阅读量')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('slug', models.SlugField(unique=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articles', to=settings.AUTH_USER_MODEL, verbose_name='作者')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.category', verbose_name='分类')),
                ('tags', models.ManyToManyField(blank=True, to='blog.Tag', verbose_name='标签集')),
                ('topics', models.ManyToManyField(blank=True, to='blog.Topic', verbose_name='话题集')),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
                'ordering': ['-created'],
                'get_latest_by': 'id',
            },
        ),
    ]
