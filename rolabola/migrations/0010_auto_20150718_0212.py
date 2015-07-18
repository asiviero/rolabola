# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_list', '0009_group_member_pending_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='member_pending_list',
            field=models.ManyToManyField(related_name='request_list_group', through='social_list.MembershipRequest', to='social_list.Player'),
        ),
        migrations.AlterField(
            model_name='membershiprequest',
            name='group',
            field=models.ForeignKey(related_name='group_request', to='social_list.Group'),
        ),
        migrations.AlterField(
            model_name='membershiprequest',
            name='member',
            field=models.ForeignKey(related_name='player_request', to='social_list.Player'),
        ),
    ]
