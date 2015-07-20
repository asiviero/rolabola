from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from rolabola.models import *
from rolabola.factories import *
from decimal import Decimal
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
        user_1.accept_request_group(group=group_1,user=user_1)

        # Check if a membership was not created
        membership_list = Membership.objects.all()
        self.assertEqual(len(membership_list),1)

        # Check if Group member_list was not updated
        self.assertEqual(len(group_1.member_list.all()),1)


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

class MatchTest(TestCase):

    def test_user_can_schedule_match(self):
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
                                            price=Decimal("20.0"))

        # Checks if a match was created
        self.assertEqual(Match.objects.all().count(),1)

        # Checks if 3 match invitations were issued
        self.assertEqual(MatchInvitation.objects.all().count(),3)

        # Check if user 4 was not invited
        self.assertEqual(MatchInvitation.objects.filter(player__pk=user_4.id).count(),0)

    def test_admin_user_schedule_match(self):
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
                                            price=Decimal("20.0"))

        # Checks if a match was not created
        self.assertEqual(Match.objects.all().count(),0)

        # Checks if no match invitations were issued
        self.assertEqual(MatchInvitation.objects.all().count(),0)


    def test_user_can_accept_match_invitation(self):
        user_1 = PlayerFactory()
        user_2 = PlayerFactory()
        user_3 = PlayerFactory()
        group_1 = user_1.create_group("Group 1", public=True)
        user_2.join_group(group_1)

        # User Schedules a match
        match = user_1.schedule_match(group_1,
                                            date=timezone.make_aware(datetime.datetime.now() + datetime.timedelta(days=3)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"))


        user_2.accept_match_invitation(match=match)
        # Check if user 3 can't confirm
        user_3.accept_match_invitation(match=match)

        self.assertEqual(len(match.get_confirmed_list()),1)
