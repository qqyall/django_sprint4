# Generated by Django 3.2.16 on 2024-01-23 04:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256, verbose_name='')),
                ('description', models.TextField(verbose_name='')),
                ('slug', models.SlugField(unique=True)),
                ('is_published', models.BooleanField(default=True, verbose_name='')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, verbose_name='')),
                ('is_published', models.BooleanField(default=True, verbose_name='')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=256, verbose_name='')),
                ('text', models.TextField(verbose_name='')),
                ('pub_date', models.DateTimeField(verbose_name='')),
                ('is_published', models.BooleanField(default=True, verbose_name='')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.category', verbose_name='')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.location', verbose_name='')),
            ],
        ),
    ]
