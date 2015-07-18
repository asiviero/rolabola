# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_list', '0003_auto_20150714_0418'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('group', models.ForeignKey(to='social_list.Group')),
                ('member', models.ForeignKey(to='social_list.Player')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='member_list',
            field=models.ManyToManyField(through='social_list.Membership', to='social_list.Player'),
        ),
    ]
