# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0013_auto_20150826_0412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='location',
            field=geoposition.fields.GeopositionField(max_length=42),
        ),
    ]
