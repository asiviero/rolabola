# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_list', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendshipRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('message', models.TextField(default='Hi, I wanna be your friend')),
                ('accepted', models.BooleanField()),
                ('user_from', models.ForeignKey(related_name='friend_ask', to='social_list.Player')),
                ('user_to', models.ForeignKey(related_name='friend_asked', to='social_list.Player')),
            ],
        ),
    ]
