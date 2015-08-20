# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0010_auto_20150801_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='automatic_confirmation',
            field=models.BooleanField(default=False),
        ),
    ]
