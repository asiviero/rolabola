# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_list', '0002_friendshiprequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='friend_request_list',
            field=models.ManyToManyField(through='social_list.FriendshipRequest', related_name='request_list', to='social_list.Player'),
        ),
        migrations.AlterField(
            model_name='friendshiprequest',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
    ]
