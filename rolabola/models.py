from django.db import models
from geoposition.fields import GeopositionField
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
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

def match_admin_required_if_user_provided(view_func):
    def _wrapped_view_func(player, *args, **kwargs):
        match = get_object_or_404(Match, pk=kwargs["match"].pk)
        if Membership.objects.filter(member__pk=player.pk,group__pk=match.pk,role=Membership.GROUP_ADMIN).count() or not "user" in kwargs.keys():
            return view_func(player, *args, **kwargs)
        pass
    return _wrapped_view_func

def match_invitation_exists(view_func):
    def _wrapped_view_func(player, *args, **kwargs):
        match = get_object_or_404(Match, pk=kwargs["match"].pk)
        player_pk = kwargs["user"].pk if "user" in kwargs.keys() else player.pk
        kwargs["user"] = Player.objects.get(pk=player_pk)
        if match.matchinvitation_set.filter(player__pk=player_pk).count() or not "user" in kwargs.keys():
            return view_func(player, *args, **kwargs)
        pass
    return _wrapped_view_func

def match_didnt_reach_max_confirmations(view_func):
    def _wrapped_view_func(player, *args, **kwargs):
        match = get_object_or_404(Match, pk=kwargs["match"].pk)
        if match.matchinvitation_set.filter(status=MatchInvitation.CONFIRMED).count() < match.max_participants:
            return view_func(player, *args, **kwargs)
        pass
    return _wrapped_view_func

def user_is_in_group(view_func):
    def _wrapped_view_func(player, *args, **kwargs):
        group = get_object_or_404(Match, pk=kwargs["group"].pk)
        if Membership.objects.get(group__pk=group.pk,member__pk=player.pk):
            return view_func(player, *args, **kwargs)
        pass
    return _wrapped_view_func


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

    @match_didnt_reach_max_confirmations
    @match_admin_required_if_user_provided
    @match_invitation_exists
    def accept_match_invitation(self,match,user=None):
        match.matchinvitation_set.get(player__pk=user.id).confirm_presence()

    @match_admin_required_if_user_provided
    @match_invitation_exists
    def refuse_match_invitation(self,match,user=None):
        match.matchinvitation_set.get(player__pk=user.id).confirm_absence()

    @match_admin_required_if_user_provided
    @match_invitation_exists
    def undo_match_invitation(self,match,user=None):
        match.matchinvitation_set.get(player__pk=user.id).undo_confirmation()

    @match_admin_required_if_user_provided
    @match_invitation_exists
    def revert_match_invitation(self,match,user=None):
        match.matchinvitation_set.get(player__pk=user.id).revert_confirmation()

    @user_is_in_group
    def toggle_automatic_confirmation_in_group(self,group):
        Membership.objects.get(member__pk=self.pk,group__pk=group.pk).toggle_automatic_confirmation()
        return Membership.objects.get(member__pk=self.pk,group__pk=group.pk).automatic_confirmation

User.player = property(lambda u: Player.objects.get_or_create(user=u)[0])


#def user_admin_required_if_user_provided()

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

@task(name="send_match_invitation_task")
def send_match_invitation_task(player,match,group):
    try:
        player = Player.objects.get(pk=player)
        match = Match.objects.get(pk=match)
        group = Group.objects.get(pk=group)
        MatchInvitation.objects.create(
            player=player,
            match=match,
            status=MatchInvitation.CONFIRMED if player.membership_set.get(group=group).automatic_confirmation else MatchInvitation.NOT_CONFIRMED
        )
        logger.info("Scheduling...")
    except Player.DoesNotExist:
        pass
    except Group.DoesNotExist:
        pass
    except Match.DoesNotExist:
        pass


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name", "public", "picture"]

def membership_post_save(sender, **kwargs):
    if kwargs["created"]:
        match_list = Match.objects.filter(group__pk=kwargs["instance"].group.pk,date__gte=datetime.date.today())
        player = kwargs["instance"].member
        for match in match_list:
            send_match_invitation_task.delay(
                player = player.pk,
                match = match.pk,
                group = match.group.pk
            )

class Membership(models.Model):
    GROUP_MEMBER = "group_member"
    GROUP_ADMIN = "group_admin"
    ROLES_IN_GROUP = (
        (GROUP_MEMBER, "Member"),
        (GROUP_ADMIN, "Admin"),
    )
    automatic_confirmation = models.BooleanField(default=False)
    member = models.ForeignKey(Player)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=30,
                                            choices=ROLES_IN_GROUP,
                                            default=GROUP_MEMBER)

    def toggle_automatic_confirmation(self):
        self.automatic_confirmation = not self.automatic_confirmation
        self.save()
post_save.connect(membership_post_save, sender=Membership)

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
            send_match_invitation_task.delay(
                player = player.pk,
                match = kwargs["instance"].pk,
                group = kwargs["instance"].group.pk
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

    def get_unanswered_list(self):
        return self.player_list.filter(matchinvitation__status=MatchInvitation.NOT_CONFIRMED)


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

    def undo_confirmation(self):
        self.status = self.NOT_CONFIRMED
        self.save()

    def revert_confirmation(self):
        self.status = self.NOT_CONFIRMED if self.status == self.CONFIRMED else self.CONFIRMED
        self.save()

class Venue(models.Model):
    quadra = models.CharField(max_length=255)
    address = models.TextField()
    location = GeopositionField()
class VenueForm(ModelForm):
    class Meta:
        model = Venue
        fields = ["quadra","location","address"]
        widgets = {"address" : forms.HiddenInput()}
