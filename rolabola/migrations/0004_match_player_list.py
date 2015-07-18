# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0003_auto_20150718_0406'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='player_list',
            field=models.ManyToManyField(to='rolabola.Player', through='rolabola.MatchInvitation'),
        ),
    ]
