# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0005_auto_20150720_0331'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='picture',
            field=models.ImageField(default='/static/img/user_generic.gif', upload_to='picture/%Y/%m/%d'),
        ),
    ]
