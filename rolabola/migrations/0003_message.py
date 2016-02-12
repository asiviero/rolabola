# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0002_match_venue'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(to='rolabola.Group')),
                ('player', models.ForeignKey(to='rolabola.Player')),
            ],
        ),
    ]
