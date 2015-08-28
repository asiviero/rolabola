# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import geoposition.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='FriendshipRequest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('message', models.TextField(default='Hi, I wanna be your friend')),
                ('accepted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('public', models.BooleanField(default=True)),
                ('picture', models.ImageField(default='/static/img/group_default.jpg', upload_to='rolabola/media/group/%Y/%m/%d')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('date', models.DateTimeField()),
                ('max_participants', models.IntegerField(default=0)),
                ('min_participants', models.IntegerField(default=0)),
                ('price', models.DecimalField(max_digits=5, decimal_places=2)),
                ('group', models.ForeignKey(to='rolabola.Group')),
            ],
        ),
        migrations.CreateModel(
            name='MatchInvitation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('status', models.CharField(default='not_confirmed', max_length='50', choices=[('confirmed', 'Confirmed'), ('not_confirmed', 'Not Confirmed'), ('absence_confirmed', 'Absence Confirmed')])),
                ('match', models.ForeignKey(to='rolabola.Match')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('automatic_confirmation', models.BooleanField(default=False)),
                ('role', models.CharField(default='group_member', max_length=30, choices=[('group_member', 'Member'), ('group_admin', 'Admin')])),
                ('group', models.ForeignKey(to='rolabola.Group')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipRequest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('accepted', models.BooleanField(default=False)),
                ('group', models.ForeignKey(related_name='group_request', to='rolabola.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('nickname', models.CharField(default='', max_length=255)),
                ('picture', models.ImageField(default='/static/img/user_generic.gif', blank=True, upload_to='picture/%Y/%m/%d')),
                ('friend_list', models.ManyToManyField(through='rolabola.Friendship', to='rolabola.Player')),
                ('friend_request_list', models.ManyToManyField(related_name='request_list', through='rolabola.FriendshipRequest', to='rolabola.Player')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('quadra', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('location', geoposition.fields.GeopositionField(max_length=42)),
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
            model_name='matchinvitation',
            name='player',
            field=models.ForeignKey(to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='match',
            name='player_list',
            field=models.ManyToManyField(through='rolabola.MatchInvitation', to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='group',
            name='member_list',
            field=models.ManyToManyField(through='rolabola.Membership', to='rolabola.Player'),
        ),
        migrations.AddField(
            model_name='group',
            name='member_pending_list',
            field=models.ManyToManyField(related_name='request_list_group', through='rolabola.MembershipRequest', to='rolabola.Player'),
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
