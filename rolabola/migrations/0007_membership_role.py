# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_list', '0006_group_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='role',
            field=models.CharField(default='group_member', choices=[('group_member', 'Member'), ('group_member', 'Admin')], max_length=30),
        ),
    ]
