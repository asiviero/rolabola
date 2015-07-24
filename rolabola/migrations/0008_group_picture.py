# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0007_auto_20150724_0407'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='picture',
            field=models.ImageField(default='/static/img/group_default.jpg', upload_to=''),
        ),
    ]
