from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

#from rolabola.signals import *

import datetime

class Player(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=255, default="")
    friend_list = models.ManyToManyField('self',through='Friendship',
                                                                        through_fields=('user_from','user_to'),
                                                                        symmetrical=False)
    friend_request_list = models.ManyToManyField('self',through='FriendshipRequest',
                                                                        through_fields=('user_to','user_from'),
                                                                        symmetrical=False,
                                                                        related_name = 'request_list')
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
            Membership.objects.create(
                member = self,
                group = group
            )
        else:
            pass
            MembershipRequest.objects.create(
                member = self,
                group = group
            )

    def create_group(self,name,public=True):
        group = Group.objects.create(
            name=name,
            public=public
        )
        Membership.objects.create(
            member=self,
            group=group,
            role=Membership.GROUP_ADMIN
        )
        return group

    def accept_request_group(self,group,user):
        if Membership.objects.filter(member__pk=self.id,role=Membership.GROUP_ADMIN):
            MembershipRequest.objects.get(group__pk=group.id,member__pk=user.id).accept()

    def schedule_match(self,group,date,max_participants,min_participants,price):
        if Membership.objects.filter(member__pk=self.id,role=Membership.GROUP_ADMIN).count():
            Match.objects.create(
                group=group,
                date=date,
                max_participants=max_participants,
                min_participants=min_participants,
                price=price
            )


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['nickname']

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.user_name = self.cleaned_data["first_name"]
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
        accepted = True
        Membership.objects.create(
            member = self.member,
            group = self.group,
            role = Membership.GROUP_MEMBER
        )
        self.save()


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

post_save.connect(match_post_save, sender=Match)



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
