# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0009_auto_20150724_0530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='picture',
            field=models.ImageField(default='/static/img/group_default.jpg', upload_to='rolabola/media/group/%Y/%m/%d'),
        ),
    ]
