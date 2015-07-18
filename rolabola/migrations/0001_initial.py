# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('friend_list', models.ManyToManyField(to='social_list.Player', through='social_list.Friendship')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='friendship',
            name='user_from',
            field=models.ForeignKey(to='social_list.Player'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='user_to',
            field=models.ForeignKey(to='social_list.Player', related_name='friend'),
        ),
    ]
