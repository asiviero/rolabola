# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0014_auto_20150826_0426'),
    ]

    operations = [
        migrations.RenameField(
            model_name='venue',
            old_name='city',
            new_name='quadra',
        ),
    ]
