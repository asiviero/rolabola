# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_list', '0005_player_nickname'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='public',
            field=models.BooleanField(default=True),
        ),
    ]
