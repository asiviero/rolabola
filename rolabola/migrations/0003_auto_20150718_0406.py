# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0002_match_matchinvitation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
