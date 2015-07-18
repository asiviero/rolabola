# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rolabola', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('date', models.DateTimeField()),
                ('max_participants', models.IntegerField(default=0)),
                ('min_participants', models.IntegerField(default=0)),
                ('price', models.DecimalField(max_digits=3, decimal_places=2)),
                ('group', models.ForeignKey(to='rolabola.Group')),
            ],
        ),
        migrations.CreateModel(
            name='MatchInvitation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('status', models.CharField(max_length='50', choices=[('confirmed', 'Confirmed'), ('not_confirmed', 'Not Confirmed'), ('absence_confirmed', 'Absence Confirmed')], default='not_confirmed')),
                ('match', models.ForeignKey(to='rolabola.Match')),
                ('player', models.ForeignKey(to='rolabola.Player')),
            ],
        ),
    ]
