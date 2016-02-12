from django.test import TestCase, Client
from django.db.models import Count, When, F
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
from rolabola.models import *
from rolabola.factories import *
from decimal import Decimal
from dateutil import rrule
import dateutil.relativedelta
from collections import Counter
import urllib

# Create your tests here.
class FriendshipTest(TestCase):

    def test_player_can_add_player(self):
        # Create two users
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()

        # Call add function
        user_1.add_user(user_2)

        # Check if a FriendshipRequest was created
        friendship_request_list = FriendshipRequest.objects.all()
        self.assertEqual(len(friendship_request_list),1)

        # Check no Friendship were created
        friendship_list = Friendship.objects.all()
        self.assertEqual(len(friendship_list),0)

        # Check if users are correct
        friendship_request = friendship_request_list[0]
        self.assertEqual(friendship_request.user_from.user.first_name,user_1.user.first_name)
        self.assertEqual(friendship_request.user_to.user.first_name,user_2.user.first_name)

        # User 2 accepts the request from User 1
        user_2.accept_request_from_friend(user_1)

        # Check if FriendshipRequest is accepted
        friendship_request_list = FriendshipRequest.objects.all()
        friendship_request = friendship_request_list[0]
        self.assertEqual(friendship_request.accepted,True)

        # Check if both users have 1 friend each
        list_user1_friends = user_1.get_friend()

        self.assertEqual(len(list_user1_friends),1)
        self.assertEqual(list_user1_friends[0].user.first_name,user_2.user.first_name)

        list_user2_friends = user_2.get_friend()
        self.assertEqual(len(list_user1_friends),1)
        self.assertEqual(list_user2_friends[0].user.first_name,user_1.user.first_name)

    def test_user_can_only_accept_friend_requests_to_himself(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()

        user_1.add_user(user_2)
        user_3.accept_request_from_friend(user_1)
        user_3.accept_request_from_friend(user_2)

        # Check if no FriendshipRequest is accepted
        friendship_request_list = FriendshipRequest.objects.all()
        friendship_request = friendship_request_list[0]
        self.assertEqual(friendship_request.accepted,False)

    def test_user_can_add_user_once(self):
        # Create two users
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()

        # Call add function
        user_1.add_user(user_2)

        # Check if a FriendshipRequest was created
        friendship_request_list = FriendshipRequest.objects.all()
        self.assertEqual(len(friendship_request_list),1)

        # Call add function again
        user_1.add_user(user_2)

        # Check if a new FriendshipRequest was not created
        friendship_request_list = FriendshipRequest.objects.all()
        self.assertEqual(len(friendship_request_list),1)

        # User 2 accepts the request from User 1
        user_2.accept_request_from_friend(user_1)

        # Call add function again
        user_1.add_user(user_2)

        # Check if a new FriendshipRequest was not created
        friendship_request_list = FriendshipRequest.objects.all()
        self.assertEqual(len(friendship_request_list),1)


class GroupTest(TestCase):

    def test_user_can_join_public_group(self):
        user_1 = PlayerFactory()
        group_1 = GroupFactory(public=True)

        user_1.join_group(group_1)

        # Check if a Membership was created
        membership_list = Membership.objects.all()
        self.assertEqual(len(membership_list),1)

        # Check if Group member_list was updated
        self.assertEqual(len(group_1.member_list.all()),1)

    def test_user_can_join_private_group(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        #group_1 = GroupFactory(public=False)
        group_1 = user_2.create_group("Group 1", public=False)

        # Check if a Membership was created
        membership_list = Membership.objects.all()
        self.assertEqual(len(membership_list),1)

        membership = membership_list.get(member__pk=user_2.id)
        self.assertEqual(membership.role,Membership.GROUP_ADMIN)

        user_1.join_group(group_1)

        # Check if a MembershipRequest was created
        membership_request_list = MembershipRequest.objects.all()
        self.assertEqual(len(membership_request_list),1)

        # Check if a Membership was not created
        membership_list = Membership.objects.all()
        self.assertEqual(len(membership_list),1)

        user_2.accept_request_group(group=group_1,user=user_1)

        # Check if a membership was created
        membership_list = Membership.objects.all()
        self.assertEqual(len(membership_list),2)

        # Check if Group member_list was updated
        self.assertEqual(len(group_1.member_list.all()),2)

    def test_user_cant_accept_if_not_admin(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        #group_1 = GroupFactory(public=False)
        group_1 = user_2.create_group("Group 1", public=False)
        user_1.join_group(group_1)
        user_1.accept_request_group(group=group_1,user=user_1)

        # Check if a membership was not created
        membership_list = Membership.objects.all()
        self.assertEqual(len(membership_list),1)

        # Check if Group member_list was not updated
        self.assertEqual(len(group_1.member_list.all()),1)

    def test_user_cant_join_group_more_than_once(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        group_1 = user_2.create_group("Group 1", public=True)
        group_2 = user_2.create_group("Group 1", public=False)

        user_1.join_group(group_1)
        user_1.join_group(group_1)
        self.assertEqual(len(group_1.member_list.all()),2)

        user_1.join_group(group_2)
        user_1.join_group(group_2)

        # Check if a single MembershipRequest was created
        membership_request_list = MembershipRequest.objects.all()
        self.assertEqual(len(membership_request_list),1)

        user_2.accept_request_group(group=group_2,user=user_1)
        user_2.accept_request_group(group=group_2,user=user_1)

        # Check if a membership was created
        membership_list = Membership.objects.all()
        self.assertEqual(len(membership_list),4)

        # Check if Group member_list was updated
        self.assertEqual(len(group_1.member_list.all()),2)



    def test_user_can_join_multiple_groups(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        group_1 = user_2.create_group("Group 1", public=True)
        group_2 = user_2.create_group("Group 1", public=True)
        user_1.join_group(group_1)
        user_1.join_group(group_2)

        membership_list = Membership.objects.filter(member__pk=user_1.pk)
        self.assertEqual(len(membership_list),2)

    def test_user_is_marked_as_admin_after_creating_group(self):
        user_1 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)

        membership_list = Membership.objects.filter(member__pk=user_1.pk, group__pk=group_1.pk)
        self.assertEqual(membership_list[0].role,Membership.GROUP_ADMIN)

    def test_user_is_not_marked_as_admin_after_joining_group(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        user_2.join_group(group_1)

        membership_list = Membership.objects.filter(member__pk=user_2.pk, group__pk=group_1.pk)
        self.assertNotEqual(membership_list[0].role,Membership.GROUP_ADMIN)

    def test_admin_can_set_group_as_private(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        c = Client()
        c.post("/login/",{"username":user_1.user.email,"password":"123456","form":"login_form"})

        response = c.post("/group/%d/private" % group_1.pk,{},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,200)

        # Reload the object
        group_1 = Group.objects.get(pk=group_1.pk)
        self.assertEqual(group_1.public,False)

    def test_non_admin_cant_set_group_as_private(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        c = Client()
        c.post("/login/",{"username":user_2.user.email,"password":"123456","form":"login_form"})

        response = c.post("/group/%d/private" % group_1.pk,{},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,403)

        # Reload the object
        group_1 = Group.objects.get(pk=group_1.pk)
        self.assertEqual(group_1.public,True)

    def test_user_cant_accept_in_group_not_managed(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()

        group_1 = user_1.create_group("Group 1", public=False)
        group_2 = user_3.create_group("Group 2", public=False)

        user_2.join_group(group_1)
        user_3.accept_request_group(group=group_1,user=user_2)

        self.assertEqual(len(group_1.member_list.all()),1)

    def test_retrieve_membership_requests(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()

        group_1 = user_1.create_group("Group 1", public=False)
        group_2 = user_1.create_group("Group 2", public=False)
        group_3 = user_1.create_group("Group 2", public=True)

        user_2.join_group(group_1)
        user_3.join_group(group_1)
        user_4.join_group(group_2)

        user_2.join_group(group_3)
        user_3.join_group(group_3)
        user_4.join_group(group_3)

        # Retrieves list of membership requests
        membership_requests = user_1.get_membership_requests_for_managed_groups()
        self.assertEqual(len(membership_requests),3)

        # Retrieves filtered version
        membership_requests = user_1.get_membership_requests_for_managed_groups(group=group_1)
        self.assertEqual(len(membership_requests),2)

        membership_requests = user_1.get_membership_requests_for_managed_groups(group=group_2)
        self.assertEqual(len(membership_requests),1)

    def test_only_managers_can_retrieve_list_of_membership_requests_to_a_group(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()

        group_1 = user_1.create_group("Group 1", public=False)
        group_2 = user_1.create_group("Group 2", public=False)

        user_2.join_group(group_1)
        user_3.join_group(group_1)
        user_4.join_group(group_2)

        group_3 = user_3.create_group("Group 3", public=False)
        user_4.join_group(group_3)

        # Retrieves list of membership requests
        membership_requests = user_2.get_membership_requests_for_managed_groups()
        self.assertEqual(len(membership_requests),0)

        membership_requests = user_3.get_membership_requests_for_managed_groups()
        self.assertEqual(len(membership_requests),1)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_user_gets_invitations_to_matches_scheduled_before_he_joined_a_group(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()

        group_1 = user_1.create_group("Group 1", public=True)

        user_2.join_group(group_1)
        user_3.join_group(group_1)

        venue_1 = VenueFactory()

        user_1.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=3)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)

        # Checks if a match was created
        self.assertEqual(Match.objects.all().count(),1)

        # Checks if 3 match invitations were issued
        self.assertEqual(MatchInvitation.objects.all().count(),3)

        # Check if user 4 was not invited
        self.assertEqual(MatchInvitation.objects.filter(player__pk=user_4.id).count(),0)

        # User 4 joins the group
        user_4.join_group(group_1)

        # Checks if user 4 got an invitation
        self.assertEqual(MatchInvitation.objects.all().count(),4)

        # Check if user 4 was not invited
        self.assertEqual(MatchInvitation.objects.filter(player__pk=user_4.id).count(),1)

    def test_retrieve_friends_in_group(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()

        group_1 = user_1.create_group("Group 1", public=True)

        user_1.add_user(user_2)
        user_1.add_user(user_3)
        user_2.accept_request_from_friend(user_1)
        user_3.accept_request_from_friend(user_1)

        user_2.join_group(group_1)
        user_3.join_group(group_1)
        user_4.join_group(group_1)

        friends = group_1.get_friends_from_user(user_1)

        self.assertEqual(len(friends),2)
        self.assertIn(user_2,friends)
        self.assertIn(user_3,friends)
        self.assertNotIn(user_4,friends)


class RegistrationTest(TestCase):

    def test_user_gets_redirected_on_home(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,settings.LOGIN_URL + "?next=/")

class SearchTest(TestCase):

    def test_user_can_search_for_users(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_2.nickname = "USER_NICKNAME"
        user_2.save()
        user_3 = PlayerFactory()
        user_3.nickname = "ANOTHER"
        user_3.save()

        c = Client()
        params = urllib.parse.urlencode({
            "qtype":"User",
            "name":user_2.user.first_name
        })
        response = c.get("/search/?%s" % params)

        self.assertContains(response,user_2.user.first_name)
        self.assertNotContains(response,user_3.user.first_name)

        params = urllib.parse.urlencode({
            "qtype":"User",
            "name":user_2.user.last_name
        })
        response = c.get("/search/?%s" % params)

        self.assertContains(response,user_2.user.last_name)
        self.assertNotContains(response,user_3.user.last_name)

        params = urllib.parse.urlencode({
            "qtype":"User",
            "name":user_2.nickname
        })
        response = c.get("/search/?%s" % params)

        self.assertContains(response,user_2.nickname)
        self.assertNotContains(response,user_3.nickname)


    def test_user_can_search_group(self):
        group_1 = GroupFactory()
        group_2 = GroupFactory()
        group_2.name = "ANOTHER"
        group_2.save()

        c = Client()
        params = urllib.parse.urlencode({
            "qtype":"Group",
            "name":group_1.name
        })
        response = c.get("/search/?%s" % params)

        self.assertContains(response,group_1.name)
        self.assertNotContains(response,group_2.name)

    def test_search_must_be_ordered_by_number_of_friends(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()
        user_5 = PlayerFactory()
        user_6 = PlayerFactory()
        user_7 = PlayerFactory()

        group_1 = user_1.create_group("Group 1", public=True)
        group_2 = user_1.create_group("Group 2", public=True)
        group_3 = user_1.create_group("Group 3", public=True)
        group_4 = user_4.create_group("Group 4", public=True)

        user_1.add_user(user_2)
        user_2.accept_request_from_friend(user_1)
        user_1.add_user(user_3)
        user_3.accept_request_from_friend(user_1)

        user_2.join_group(group_2)
        user_2.join_group(group_3)
        user_3.join_group(group_2)
        user_5.join_group(group_4)
        user_6.join_group(group_4)
        user_7.join_group(group_4)

        results = Group.objects.filter(
            Q(name__icontains="Group") &
            Q(membership__member__in=[user_1.pk,user_2.pk])
        )
        # print(results)

        # Search will be performed
        results = Group.objects.filter(
            Q(name__icontains="Group")
        ).annotate(member_list_count=Count(Q(membership__member__in=([x.pk for x in user_1.friend_list.all()])),distinct=True)).order_by("-member_list_count")
        # print(results)

        self.assertEqual(results[0].pk,group_2.pk)
        self.assertEqual(results[1].pk,group_3.pk)
        self.assertEqual(results[2].pk,group_1.pk)

class MatchTest(TestCase):

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_user_can_schedule_match(self):
        venue_1 = VenueFactory()
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)

        user_2.join_group(group_1)
        user_3.join_group(group_1)

        # User Schedules a match
        user_1.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=3)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)

        # Checks if a match was created
        self.assertEqual(Match.objects.all().count(),1)

        # Checks if 3 match invitations were issued
        self.assertEqual(MatchInvitation.objects.all().count(),3)

        # Check if user 4 was not invited
        self.assertEqual(MatchInvitation.objects.filter(player__pk=user_4.id).count(),0)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_nonadmin_user_cant_schedule_match(self):
        venue_1 = VenueFactory()
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)

        user_2.join_group(group_1)
        user_3.join_group(group_1)

        # User Schedules a match
        user_2.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=3)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)

        # Checks if a match was not created
        self.assertEqual(Match.objects.all().count(),0)

        # Checks if no match invitations were issued
        self.assertEqual(MatchInvitation.objects.all().count(),0)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_admin_user_can_schedule_match_only_for_his_own_groups(self):
        venue_1 = VenueFactory()
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        group_2 = user_2.create_group("Group 1", public=True)

        user_2.join_group(group_1)
        user_3.join_group(group_1)

        # User Schedules a match
        user_2.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=3)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)

        # Checks if a match was not created
        self.assertEqual(Match.objects.all().count(),0)

        # Checks if no match invitations were issued
        self.assertEqual(MatchInvitation.objects.all().count(),0)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_schedule_until(self):
        venue_1 = VenueFactory()
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        user_2.join_group(group_1)
        user_3.join_group(group_1)
        user_1.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1,
                                            until=timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=500)))

        rule = rrule.rrule(rrule.DAILY,
                   dtstart=timezone.make_aware(datetime.datetime.now()),
                   until=timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=500)))
        total_matches = dict(Counter(d.strftime('%A') for d in rule)).get(datetime.datetime.now().strftime("%A"))
        # Checks if matches for all weekdays were created
        self.assertEqual(Match.objects.all().count(),total_matches)

        # Checks if no match invitations were issued
        self.assertEqual(MatchInvitation.objects.all().count(),3*total_matches)

class CalendarTest(TestCase):

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_list_of_match_invitations_for_user(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        group_2 = user_1.create_group("Group 2", public=True)
        group_3 = user_1.create_group("Group 3", public=True)
        user_2.join_group(group_1)
        user_2.join_group(group_2)
        user_2.join_group(group_3)
        user_3.join_group(group_1)
        user_3.join_group(group_2)
        user_4.join_group(group_1)
        venue_1 = VenueFactory()
        user_1.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)
        user_1.schedule_match(group_2,
                                            date=timezone.make_aware(datetime.datetime.now()+datetime.timedelta(days=1)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)
        user_1.schedule_match(group_3,
                                            date=timezone.make_aware(datetime.datetime.now()+datetime.timedelta(days=2)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)
        match_invitation_list_user_1 = user_1.get_match_invitations()
        self.assertEqual(len(match_invitation_list_user_1),3)
        match_invitation_list_user_2 = user_2.get_match_invitations()
        self.assertEqual(len(match_invitation_list_user_2),3)
        match_invitation_list_user_3 = user_3.get_match_invitations()
        self.assertEqual(len(match_invitation_list_user_3),2)
        match_invitation_list_user_4 = user_4.get_match_invitations()
        self.assertEqual(len(match_invitation_list_user_4),1)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_user_should_not_see_invitations_to_groups_he_is_not_a_member(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        group_2 = user_1.create_group("Group 2", public=False)
        user_2.join_group(group_1)
        user_2.join_group(group_2)
        user_1.accept_request_group(group=group_2,user=user_2)
        user_3.join_group(group_1)
        user_3.join_group(group_2)
        venue_1 = VenueFactory()

        user_1.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)
        user_1.schedule_match(group_2,
                                            date=timezone.make_aware(datetime.datetime.now()+datetime.timedelta(days=1)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)

        match_invitation_list_user_1 = user_1.get_match_invitations()
        self.assertEqual(len(match_invitation_list_user_1),2)
        match_invitation_list_user_2 = user_2.get_match_invitations()
        self.assertEqual(len(match_invitation_list_user_2),2)
        match_invitation_list_user_3 = user_3.get_match_invitations()
        self.assertEqual(len(match_invitation_list_user_3),1)
        match_invitation_list_user_4 = user_4.get_match_invitations()
        self.assertEqual(len(match_invitation_list_user_4),0)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_filter_match_invitation_by_dates(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        venue_1 = VenueFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        user_2.join_group(group_1)
        user_1.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1,
                                            until=timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=500)))
        user_1.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now()) + datetime.timedelta(days=1),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1,
                                            until=timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=500)))

        match_invitation_list_user_1 = user_1.get_match_invitations(
                                                                                                        start_date=(timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=-2))),
                                                                                                        end_date=(timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=+10))),
                                                                                                    )
        self.assertEqual(len(match_invitation_list_user_1),4)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_filter_match_invitation_by_group(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        group_2 = user_1.create_group("Group 2", public=True)
        user_2.join_group(group_1)
        user_2.join_group(group_2)
        venue_1 = VenueFactory()
        user_1.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)
        user_1.schedule_match(group_2,
                                            date=timezone.make_aware(datetime.datetime.now()) + datetime.timedelta(days=1),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=venue_1)

        match_invitation_list_user_2 = user_2.get_match_invitations(group=group_1)
        self.assertEqual(len(match_invitation_list_user_2),1)

    def test_user_cant_retrieve_monthly_calendar_from_group_he_is_not_a_member(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        user_4 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        group_2 = user_1.create_group("Group 2", public=False)
        user_2.join_group(group_1)
        user_2.join_group(group_2)
        user_1.accept_request_group(group=group_2,user=user_2)
        user_3.join_group(group_1)
        user_3.join_group(group_2)

        c = Client()
        c.post("/login/",{"username":user_4.user.email,"password":"123456","form":"login_form"})
        response = c.post(reverse("calendar-update-monthly"),{"group":group_2.pk,"year":"2015","month":"9","day":"5"},HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code,403)

@override_settings(CELERY_ALWAYS_EAGER=True)
class MatchConfirmationTest(TestCase):

    def setUp(self):
        self.user_1 = PlayerFactory()
        self.user_2 = PlayerFactory()
        self.user_3 = PlayerFactory()
        self.user_4 = PlayerFactory()
        self.group_1 = self.user_1.create_group("Group 1", public=True)
        self.group_2 = self.user_1.create_group("Group 1", public=False)
        self.group_3 = self.user_2.create_group("Group 1", public=False)
        self.user_2.join_group(self.group_1)
        self.user_3.join_group(self.group_1)
        self.venue_1 = VenueFactory()
        self.match = self.user_1.schedule_match(self.group_1,
                                            date=timezone.make_aware(datetime.datetime.now()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1)
        self.match_private = self.user_1.schedule_match(self.group_2,
                                            date=timezone.make_aware(datetime.datetime.now()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1)
        self.match_third = self.user_2.schedule_match(self.group_3,
                                            date=timezone.make_aware(datetime.datetime.now()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1)
        self.match_restricted = self.user_1.schedule_match(self.group_1,
                                            date=timezone.make_aware(datetime.datetime.now())+dateutil.relativedelta.relativedelta(hour=1),
                                            max_participants=2,
                                            min_participants=1,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1)



    def test_user_can_accept_match_invitation(self):

        self.user_2.accept_match_invitation(match=self.match)
        # Check if user 3 can't confirm
        self.user_3.accept_match_invitation(match=self.match)
        # Check if user 4 can't confirm
        self.user_4.accept_match_invitation(match=self.match)
        self.user_4.refuse_match_invitation(match=self.match)

        self.assertEqual(len(self.match.get_confirmed_list()),2)

    def test_user_can_refuse_match_confirmation(self):

        self.user_2.accept_match_invitation(match=self.match)
        # Check if user 3 can't confirm
        self.user_3.refuse_match_invitation(match=self.match)
        # Check if user 4 can't confirm
        self.user_4.accept_match_invitation(match=self.match)
        self.user_4.refuse_match_invitation(match=self.match)

        self.assertEqual(len(self.match.get_confirmed_list()),1)
        self.assertEqual(len(self.match.get_refused_list()),1)

    def test_admin_can_perform_actions_on_any_user(self):

        self.user_1.accept_match_invitation(match=self.match,user=self.user_2)
        self.user_1.refuse_match_invitation(match=self.match,user=self.user_3)
        # Check if user 4 can't confirm
        self.user_1.accept_match_invitation(match=self.match,user=self.user_4)
        self.user_1.refuse_match_invitation(match=self.match,user=self.user_4)

        self.assertEqual(len(self.match.get_confirmed_list()),1)
        self.assertEqual(len(self.match.get_refused_list()),1)

    def test_user_cant_perform_actions_on_any_user(self):

        self.user_3.accept_match_invitation(match=self.match,user=self.user_2)
        self.user_2.refuse_match_invitation(match=self.match,user=self.user_3)
        # Check if user 4 can't confirm
        self.user_4.accept_match_invitation(match=self.match,user=self.user_4)
        self.user_4.refuse_match_invitation(match=self.match,user=self.user_4)

        self.assertEqual(len(self.match.get_confirmed_list()),0)
        self.assertEqual(len(self.match.get_refused_list()),0)

    def test_user_can_undo_own_confirmation(self):
        self.user_2.accept_match_invitation(match=self.match)
        self.user_3.accept_match_invitation(match=self.match)

        self.user_2.undo_match_invitation(match=self.match)
        self.user_2.undo_match_invitation(match=self.match_private)
        self.user_2.undo_match_invitation(match=self.match, user=self.user_3)

        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        user_3_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_3.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.NOT_CONFIRMED)
        self.assertEqual(user_3_invitation.status,MatchInvitation.CONFIRMED)

    def test_admin_can_undo_confirmations_in_his_group(self):
        self.user_2.accept_match_invitation(match=self.match)
        self.user_2.accept_match_invitation(match=self.match_third)

        self.user_1.undo_match_invitation(match=self.match, user=self.user_2)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)

        self.assertEqual(user_2_invitation.status,MatchInvitation.NOT_CONFIRMED)

        self.user_1.undo_match_invitation(match=self.match_third, user=self.user_2)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match_third.pk,player__pk=self.user_2.pk)

        self.assertEqual(user_2_invitation.status,MatchInvitation.CONFIRMED)

    def test_user_can_only_confirm_presence_if_match_hasnt_reached_max_confirmations(self):
        self.user_1.accept_match_invitation(match=self.match_restricted)
        self.user_2.accept_match_invitation(match=self.match_restricted)
        self.user_3.accept_match_invitation(match=self.match_restricted)

        user_1_invitation = MatchInvitation.objects.get(match__pk=self.match_restricted.pk,player__pk=self.user_1.pk)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match_restricted.pk,player__pk=self.user_2.pk)
        user_3_invitation = MatchInvitation.objects.get(match__pk=self.match_restricted.pk,player__pk=self.user_3.pk)

        self.assertEqual(user_1_invitation.status,MatchInvitation.CONFIRMED)
        self.assertEqual(user_2_invitation.status,MatchInvitation.CONFIRMED)
        self.assertEqual(user_3_invitation.status,MatchInvitation.NOT_CONFIRMED)

        self.assertEqual(len(self.match_restricted.get_confirmed_list()),self.match_restricted.max_participants)

    def test_user_can_revert_his_own_status(self):
        self.user_2.accept_match_invitation(match=self.match)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.CONFIRMED)

        self.user_2.revert_match_invitation(match=self.match)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.NOT_CONFIRMED)

        self.user_2.revert_match_invitation(match=self.match)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.CONFIRMED)

        self.user_2.revert_match_invitation(match=self.match)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.NOT_CONFIRMED)

        self.user_2.refuse_match_invitation(match=self.match)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.ABSENCE_CONFIRMED)

        self.user_2.revert_match_invitation(match=self.match)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.NOT_CONFIRMED)
        

    def test_user_cant_revert_other_user_status(self):
        self.user_2.accept_match_invitation(match=self.match)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.CONFIRMED)
        self.user_3.revert_match_invitation(match=self.match,user=self.user_2)
        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.CONFIRMED)

    def test_admin_can_revert_anyone_in_his_groups_status(self):
        self.user_2.accept_match_invitation(match=self.match)
        self.user_2.accept_match_invitation(match=self.match_third)

        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.CONFIRMED)

        self.user_1.revert_match_invitation(match=self.match,user=self.user_2)
        self.user_1.revert_match_invitation(match=self.match_third,user=self.user_2)

        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.NOT_CONFIRMED)

        user_2_invitation = MatchInvitation.objects.get(match__pk=self.match_third.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.CONFIRMED)

    def test_automatic_confirmation_in_group(self):
        self.user_2.toggle_automatic_confirmation_in_group(group=self.group_1)
        new_match = self.user_1.schedule_match(self.group_1,
                                            date=timezone.make_aware(datetime.datetime.now()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1)
        user_2_invitation = MatchInvitation.objects.get(match__pk=new_match.pk,player__pk=self.user_2.pk)
        self.assertEqual(user_2_invitation.status,MatchInvitation.CONFIRMED)
        user_3_invitation = MatchInvitation.objects.get(match__pk=new_match.pk,player__pk=self.user_3.pk)
        self.assertEqual(user_3_invitation.status,MatchInvitation.NOT_CONFIRMED)

class MessageTest(TestCase):

    def setUp(self):
        self.user_1 = PlayerFactory()
        self.user_2 = PlayerFactory()
        self.user_3 = PlayerFactory()
        self.user_4 = PlayerFactory()
        self.group_1 = self.user_1.create_group("Group 1", public=True)
        self.group_2 = self.user_1.create_group("Group 2", public=False)
        self.user_2.join_group(self.group_1)
        self.user_2.join_group(self.group_2)
        self.user_1.accept_request_group(group=self.group_2,user=self.user_2)
        self.user_3.join_group(self.group_1)
        self.user_3.join_group(self.group_2)

        # Message sending
        self.user_1.send_message_group(group=self.group_1,message="test message 1")
        self.user_2.send_message_group(group=self.group_1,message="test message 2")
        self.user_3.send_message_group(group=self.group_1,message="test message 3")
        self.user_1.send_message_group(group=self.group_2,message="test message 1")
        self.user_2.send_message_group(group=self.group_2,message="test message 2")
        self.user_3.send_message_group(group=self.group_2,message="test message 3")

    def test_user_can_send_message(self):

        messages_in_group_1 = self.group_1.get_messages()
        self.assertEqual(len(messages_in_group_1),3)
        self.assertEqual(messages_in_group_1[0].message,"test message 3")
        self.assertEqual(messages_in_group_1[1].message,"test message 2")
        self.assertEqual(messages_in_group_1[2].message,"test message 1")

        messages_in_group_2 = self.group_2.get_messages()
        self.assertEqual(len(messages_in_group_2),2)
        self.assertEqual(messages_in_group_2[0].message,"test message 2")
        self.assertEqual(messages_in_group_2[1].message,"test message 1")

    def test_message_deletion_user(self):
        messages_in_group_1 = self.group_1.get_messages()
        c = Client()

        c.post("/login/",{"username":self.user_3.user.email,"password":"123456","form":"login_form"})
        response = c.post("/message/%d/delete" % messages_in_group_1[0].pk,{},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,200)

        messages_in_group_1 = self.group_1.get_messages()
        self.assertEqual(len(messages_in_group_1),2)

        response = c.post("/message/%d/delete" % messages_in_group_1[0].pk,{},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,403)

        messages_in_group_1 = self.group_1.get_messages()
        self.assertEqual(len(messages_in_group_1),2)

        messages_in_group_2 = self.group_2.get_messages()
        response = c.post("/message/%d/delete" % messages_in_group_1[0].pk,{},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,403)

    def test_message_deletion_admin(self):
        messages_in_group_1 = self.group_1.get_messages()
        c = Client()

        c.post("/login/",{"username":self.user_1.user.email,"password":"123456","form":"login_form"})
        response = c.post("/message/%d/delete" % messages_in_group_1[0].pk,{},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,200)

        messages_in_group_1 = self.group_1.get_messages()
        self.assertEqual(len(messages_in_group_1),2)

        response = c.post("/message/%d/delete" % messages_in_group_1[0].pk,{},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,200)

        messages_in_group_1 = self.group_1.get_messages()
        self.assertEqual(len(messages_in_group_1),1)

        messages_in_group_2 = self.group_2.get_messages()
        response = c.post("/message/%d/delete" % messages_in_group_2[0].pk,{},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,200)
        messages_in_group_2 = self.group_2.get_messages()
        self.assertEqual(len(messages_in_group_2),1)
