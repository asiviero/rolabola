# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='FriendshipRequest',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('message', models.TextField(default='Hi, I wanna be your friend')),
                ('accepted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('public', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('role', models.CharField(default='group_member', choices=[('group_member', 'Member'), ('group_member', 'Admin')], max_length=30)),
                ('group', models.ForeignKey(to='rolabola.Group')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipRequest',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('accepted', models.BooleanField(default=False)),
                ('group', models.ForeignKey(related_name='group_request', to='rolabola.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('nickname', models.CharField(default='', max_length=255)),
                ('friend_list', models.ManyToManyField(through='rolabola.Friendship', to='rolabola.Player')),
                ('friend_request_list', models.ManyToManyField(through='rolabola.FriendshipRequest', related_name='request_list', to='rolabola.Player')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='membershiprequest',
            name='member',
            field=models.ForeignKey(related_name='player_request', to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='membership',
            name='member',
            field=models.ForeignKey(to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='group',
            name='member_list',
            field=models.ManyToManyField(through='rolabola.Membership', to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='group',
            name='member_pending_list',
            field=models.ManyToManyField(through='rolabola.MembershipRequest', related_name='request_list_group', to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='friendshiprequest',
            name='user_from',
            field=models.ForeignKey(related_name='friend_ask', to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='friendshiprequest',
            name='user_to',
            field=models.ForeignKey(related_name='friend_asked', to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='user_from',
            field=models.ForeignKey(to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='friendship',
            name='user_to',
            field=models.ForeignKey(related_name='friend', to='rolabola.Player'),
        ),
    ]
