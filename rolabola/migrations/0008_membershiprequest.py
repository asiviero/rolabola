# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social_list', '0007_membership_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipRequest',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('group', models.ForeignKey(to='social_list.Group')),
                ('member', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
