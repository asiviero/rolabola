# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0006_player_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='picture',
            field=models.ImageField(upload_to='picture/%Y/%m/%d', default='/static/img/user_generic.gif', blank=True),
        ),
    ]
