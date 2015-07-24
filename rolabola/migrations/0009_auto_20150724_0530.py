# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0008_group_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='picture',
            field=models.ImageField(upload_to='group/%Y/%m/%d', default='/static/img/group_default.jpg'),
        ),
    ]
