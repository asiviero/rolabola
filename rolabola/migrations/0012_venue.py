# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import location_field.models.plain


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0011_membership_automatic_confirmation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('address', models.CharField(max_length=255)),
                ('location', location_field.models.plain.PlainLocationField(max_length=63)),
            ],
        ),
    ]
