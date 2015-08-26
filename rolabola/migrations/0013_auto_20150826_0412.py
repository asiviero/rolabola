# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0012_venue'),
    ]

    operations = [
        migrations.RenameField(
            model_name='venue',
            old_name='address',
            new_name='city',
        ),
    ]
