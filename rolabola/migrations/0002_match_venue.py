# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='venue',
            field=models.ForeignKey(null=True, to='rolabola.Venue', blank=True),
        ),
    ]
