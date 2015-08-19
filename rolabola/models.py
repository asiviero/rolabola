from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.utils import timezone
from celery.decorators import task
from celery.utils.log import get_task_logger
from rolabola.models import *
logger = get_task_logger(__name__)

#import os
from social import settings

import datetime
import json

class Player(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=255, default="")
    picture = models.ImageField(upload_to="picture/%Y/%m/%d", default="/static/img/user_generic.gif", blank=True)
    friend_list = models.ManyToManyField('self',through='Friendship',
                                                                        through_fields=('user_from','user_to'),
                                                                        symmetrical=False)
    friend_request_list = models.ManyToManyField('self',through='FriendshipRequest',
                                                                        through_fields=('user_to','user_from'),
                                                                        symmetrical=False,
                                                                        related_name = 'request_list')

    def fetch_picture(self):
        fb_uid = SocialAccount.objects.filter(user_id=self.user.id, provider='facebook')
        if len(fb_uid):
            return "http://graph.facebook.com/{}/picture".format(fb_uid[0].uid)
        if self.picture == Player._meta.get_field("picture").get_default():
            return self.picture
        return settings.MEDIA_URL + str(self.picture)

    def __str__(self):
        return u"%s %s (%s)" % (self.user.first_name,self.user.last_name,self.nickname)

    def add_user(self,friend,message=""):

        # Check if there isn't a FriendshipRequest involving this user or the possible friend
        if FriendshipRequest.objects.filter(
            (Q(user_from=self) & Q(user_to=friend)) |
            (Q(user_to=self) & Q(user_from=friend))
        ).count() == 0:
            FriendshipRequest.objects.create(
                user_from = self,
                user_to = friend,
                message = message,
            )

    def get_friend(self,friend_id=None):
        return self.friend_list.all()

    def accept_request_from_friend(self,friend):
        try:
            FriendshipRequest.objects.get(user_from=friend,user_to=self).accept()
        except FriendshipRequest.DoesNotExist:
            pass

    def join_group(self,group):
        if group.public:
            # Check if a membership object exists
            if not Membership.objects.filter(member__pk=self.id,group__pk=group.id).count():
                return Membership.objects.create(
                    member = self,
                    group = group
                )
        else:
            # Check if a membershiprequest object exists
            if not MembershipRequest.objects.filter(member__pk=self.id,group__pk=group.id).count():
                return MembershipRequest.objects.create(
                    member = self,
                    group = group
                )

    def create_group(self,name,public=True,picture=None):
        group = Group.objects.create(
            name=name,
            public=public,
            picture=picture
        )
        Membership.objects.create(
            member=self,
            group=group,
            role=Membership.GROUP_ADMIN
        )
        return group

    def accept_request_group(self,group,user):
        if Membership.objects.filter(member__pk=self.id,group__pk=group.pk,role=Membership.GROUP_ADMIN).count() \
        and MembershipRequest.objects.filter(group__pk=group.id,member__pk=user.id).count():
            MembershipRequest.objects.get(group__pk=group.id,member__pk=user.id).accept()

    def reject_request_group(self,group,user):
        if Membership.objects.filter(member__pk=self.id,group__pk=group.pk,role=Membership.GROUP_ADMIN).count() \
        and MembershipRequest.objects.filter(group__pk=group.id,member__pk=user.id).count():
            MembershipRequest.objects.get(group__pk=group.id,member__pk=user.id).reject()

    def get_membership_requests_for_managed_groups(self,group=None):
        if group is None:
            admin_membership_list = Membership.objects.filter(member__pk=self.id,role=Membership.GROUP_ADMIN)
            group_list = [x.group.pk for x in admin_membership_list]
        else:
            group_list = [group.pk]
        return MembershipRequest.objects.filter(
            group__pk__in=group_list
        )

    def schedule_match(self,group,date,max_participants,min_participants,price,until=None):
        if not until is None:
            base_date = date + datetime.timedelta(days=7)
            while base_date < until:
                schedule_match_task.delay(
                    player=self.pk,
                    group=group.pk,
                    date={"year":base_date.year,"month":base_date.month,"day":base_date.day},
                    max_participants=max_participants,
                    min_participants=min_participants,
                    price=str(price)
                )
                base_date += datetime.timedelta(days=7)
        if Membership.objects.filter(member__pk=self.id,group__pk=group.pk,role=Membership.GROUP_ADMIN).count():
            return Match.objects.create(
                group=group,
                date=date,
                max_participants=max_participants,
                min_participants=min_participants,
                price=price
            )

    def get_match_invitations(self,start_date=None,end_date=None,group=None):
        match_invitation_list = MatchInvitation.objects.filter(player__pk=self.pk)
        if not start_date is None:
            match_invitation_list = match_invitation_list.filter(match__date__gte=start_date)
        if not end_date is None:
            match_invitation_list = match_invitation_list.filter(match__date__lte=end_date)
        if not group is None:
            match_invitation_list = match_invitation_list.filter(match__group__pk=group.pk)
        return match_invitation_list

    def accept_match_invitation(self,match,user=None):
        if not user is None and user.pk != self.pk:
            # Need to check if user is admin of match group
            if not Membership.objects.filter(member__pk=self.id,role=Membership.GROUP_ADMIN,group__pk=match.group.pk).count():
                return
        else :
            user = self
        try:
            if match.matchinvitation_set.get(player__pk=user.id):
                match.matchinvitation_set.get(player__pk=user.id).confirm_presence()
        except MatchInvitation.DoesNotExist as e:
            pass

    def refuse_match_invitation(self,match,user=None):
        if not user is None and user.pk != self.pk:
            # Need to check if user is admin of match group
            if not Membership.objects.filter(member__pk=self.id,role=Membership.GROUP_ADMIN,group__pk=match.group.pk).count():
                return
        else :
            user = self
        try:
            if match.matchinvitation_set.get(player__pk=self.id):
                match.matchinvitation_set.get(player__pk=self.id).confirm_absence()
        except MatchInvitation.DoesNotExist as e:
            pass

User.player = property(lambda u: Player.objects.get_or_create(user=u)[0])


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['nickname']

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email','first_name','last_name','password1','password2']

    def clean_user_name( self ):
            email = self.cleaned_data['email']
            return email
    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.username = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
class Friendship(models.Model):

    user_from = models.ForeignKey(Player)
    user_to = models.ForeignKey(Player,related_name="friend")

class FriendshipRequest(models.Model):
    user_from = models.ForeignKey(Player,related_name="friend_ask")
    user_to = models.ForeignKey(Player,related_name="friend_asked")
    message = models.TextField(default="Hi, I wanna be your friend")
    accepted = models.BooleanField(default = False)
    def accept(self):
        # Creates two Friendship
        Friendship.objects.create(
            user_from = self.user_from,
            user_to = self.user_to
        )

        Friendship.objects.create(
            user_from = self.user_to,
            user_to = self.user_from
        )
        self.accepted = True
        self.save()

class Group(models.Model):
    name = models.CharField(max_length = 255)
    member_list = models.ManyToManyField(Player,through='Membership')
    member_pending_list = models.ManyToManyField(Player,through='MembershipRequest',
                                                                                    related_name = "request_list_group")
    public = models.BooleanField(default=True)
    picture = models.ImageField(default="/static/img/group_default.jpg",upload_to="rolabola/media/group/%Y/%m/%d")

    def __str__(self):
        return u"%s" % self.name

    def fetch_picture(self):
        if self.picture == Group._meta.get_field("picture").get_default():
            return self.picture
        return settings.MEDIA_URL + str(self.picture)

@task(name="schedule_match_task")
def schedule_match_task(player,group,date,max_participants,min_participants,price):
    try:
        logger.info("Scheduling...")
        player = Player.objects.get(pk=player)
        group = Group.objects.get(pk=group)
        date = timezone.make_aware(datetime.datetime(date.get("year"),date.get("month"),date.get("day")))
        player.schedule_match(group,date,max_participants,min_participants,price)
    except Player.DoesNotExist:
        pass
    except Group.DoesNotExist:
        pass


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name", "public", "picture"]

class Membership(models.Model):
    GROUP_MEMBER = "group_member"
    GROUP_ADMIN = "group_admin"
    ROLES_IN_GROUP = (
        (GROUP_MEMBER, "Member"),
        (GROUP_ADMIN, "Admin"),
    )
    member = models.ForeignKey(Player)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=30,
                                            choices=ROLES_IN_GROUP,
                                            default=GROUP_MEMBER)

class MembershipRequest(models.Model):
    member = models.ForeignKey(Player, related_name="player_request")
    group = models.ForeignKey(Group, related_name = "group_request")
    accepted = models.BooleanField(default=False)
    def accept(self):
        Membership.objects.create(
            member = self.member,
            group = self.group,
            role = Membership.GROUP_MEMBER
        )
        self.delete()
    def reject(self):
        self.delete()

def match_post_save(sender, **kwargs):
    if kwargs["created"]:
        for player in kwargs["instance"].group.member_list.all():
            MatchInvitation.objects.create(
                player=player,
                match=kwargs["instance"],
            )

class Match(models.Model):
    date = models.DateTimeField()
    max_participants = models.IntegerField(default=0)
    min_participants = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=5,decimal_places=2)
    group = models.ForeignKey(Group)
    player_list = models.ManyToManyField(Player,through='MatchInvitation')

    def get_confirmed_list(self):
        return self.player_list.filter(matchinvitation__status=MatchInvitation.CONFIRMED)

    def get_refused_list(self):
        return self.player_list.filter(matchinvitation__status=MatchInvitation.ABSENCE_CONFIRMED)


    def __str__(self):
        return u"%s (%s)" % (self.group.name,self.date.strftime("%d/%m/%Y"))

post_save.connect(match_post_save, sender=Match)

class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ["date","max_participants","min_participants","price"]
    until_end_of_month = forms.BooleanField(label="Schedule until the end of the month",required=False)
    until_end_of_year = forms.BooleanField(label="Schedule until the end of the year",required=False)
    def clean(self):
        super(MatchForm,self).clean()
        until_end_of_month = self.cleaned_data.get("until_end_of_month")
        until_end_of_year = self.cleaned_data.get("until_end_of_year")
        return self.cleaned_data

class MatchInvitation(models.Model):
    CONFIRMED = "confirmed"
    NOT_CONFIRMED = "not_confirmed"
    ABSENCE_CONFIRMED = "absence_confirmed"
    STATUS_CHOICES = (
        (CONFIRMED, "Confirmed"),
        (NOT_CONFIRMED, "Not Confirmed"),
        (ABSENCE_CONFIRMED, "Absence Confirmed"),
    )
    player = models.ForeignKey(Player)
    match = models.ForeignKey(Match)
    status = models.CharField(max_length="50",
                                                choices=STATUS_CHOICES,
                                                default=NOT_CONFIRMED)
    def confirm_presence(self):
        self.status = self.CONFIRMED
        self.save()

    def confirm_absence(self):
        self.status = self.ABSENCE_CONFIRMED
        self.save()
