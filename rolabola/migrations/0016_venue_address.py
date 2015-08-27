# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0015_auto_20150826_0432'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='address',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
