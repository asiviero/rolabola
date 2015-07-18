# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social_list', '0008_membershiprequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='member_pending_list',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='social_list.MembershipRequest'),
        ),
    ]
