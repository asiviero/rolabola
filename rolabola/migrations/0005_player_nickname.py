# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_list', '0004_auto_20150714_0520'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='nickname',
            field=models.CharField(default='', max_length=255),
        ),
    ]
