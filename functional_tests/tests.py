from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase, RequestFactory
from django.test.utils import override_settings
from django.utils import timezone
from django.contrib.auth import authenticate
from django.test import Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from decimal import Decimal
from rolabola.factories import *
from rolabola.models import *
import datetime
import dateutil
import dateutil.relativedelta
import time

class NewVisitorTest(StaticLiveServerTestCase):

    user_1 = None
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1.5)

        # Create a user
        self.user_1 = PlayerFactory()
        self.user_1.user.set_password("123456")
        self.user_1.user.save()

    def tearDown(self):
        self.browser.quit()

    def test_registration(self):

        # User enters website, sees login and registration form
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_registration = self.browser.find_element_by_id('form_registration')

        # User has no login yet, so he proceeds to fill the registration
        form_registration.find_element_by_id("id_nickname").send_keys("Nickname")
        form_registration.find_element_by_id("id_first_name").send_keys("First Name")
        form_registration.find_element_by_id("id_last_name").send_keys("Last Name")
        form_registration.find_element_by_id("id_email").send_keys("email@email.com")
        form_registration.find_element_by_id("id_password1").send_keys("123456")
        form_registration.find_element_by_id("id_password2").send_keys("123456")

        # User hits the submit button and waits for success
        form_registration.find_element_by_css_selector("input[type='submit']").click()

        redirected_url = self.browser.current_url
        self.assertEqual(redirected_url,self.live_server_url + "/")


    def test_profile_page(self):

        # Existing user access the website, sees login and registration form
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_registration = self.browser.find_element_by_id('form_registration')

        # User fills his login info
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.email)
        form_login.find_element_by_id("id_password").send_keys("123456")

        # User hits the submit button and waits for success
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # In the side pane, user sees a generic picture, name and nickname
        side_pane = self.browser.find_element_by_class_name('side-pane')

        img_user_profile = side_pane.find_element_by_css_selector("img.img-profile")
        full_name = "%s %s" % (self.user_1.user.first_name,self.user_1.user.last_name)
        self.assertIn(full_name,side_pane.text)
        self.assertIn(self.user_1.nickname,side_pane.text)

        # Group list is still empty
        group_list_wrapper = side_pane.find_element_by_id("group-list-wrapper")
        self.assertEqual(len(group_list_wrapper.find_elements_by_tag_name("li")),1)
        self.assertIn("No groups yet",group_list_wrapper.text)

        # In main body, he will see a calendar view... (maybe this is a separate test)



    def test_logout(self):

        # Existing user access the website, sees login and registration form
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_registration = self.browser.find_element_by_id('form_registration')

        # User fills his login info
        # User fills his login info
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.email)
        form_login.find_element_by_id("id_password").send_keys("123456")

        # User hits the submit button and waits for success
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User sees a logout link, clicks it
        self.browser.find_element_by_link_text("Logout").click()

        time.sleep(1)

        # User is redirected to main page, sees both forms again
        form_login = self.browser.find_element_by_id('form_login')
        form_registration = self.browser.find_element_by_id('form_registration')

        pass

class SearchTest(StaticLiveServerTestCase):

    user_1 = None
    user_2 = None
    group_1 = None

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1.5)

        # Create a user
        self.user_1 = PlayerFactory()
        self.user_1.user.set_password("123456")
        self.user_1.user.save()

        self.user_2 = PlayerFactory()
        self.user_2.user.set_password("123456")
        self.user_2.nickname = "NICKNAME"
        self.user_2.save()
        self.user_2.user.save()

        # Create group
        self.group_1 = self.user_2.create_group("%s's Public Group" % (self.user_2.nickname),public=True)
        self.group_2 = self.user_2.create_group("%s's Private Group" % (self.user_2.nickname),public=False)
        self.group_3 = self.user_2.create_group("%s's Joined Group" % (self.user_2.nickname),public=True)
        self.group_4 = self.user_2.create_group("%s's Private Joined Group" % (self.user_2.nickname),public=False)
        self.user_1.join_group(self.group_3)
        self.user_1.join_group(self.group_4)

    def tearDown(self):
        self.browser.quit()

    def test_user_search(self):

        # User access site and logs in
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User sees a search box
        form_search = self.browser.find_element_by_id('form_search')

        # User types in another user name
        form_search.find_element_by_css_selector("input[type='text']").send_keys(self.user_2.nickname)
        form_search.find_element_by_css_selector("input[type='text']").send_keys(Keys.ENTER)

        # User gets redirected to registration page, where he sees
        # the results of his search
        time.sleep(1)
        redirected_url = self.browser.current_url

        self.assertRegexpMatches(redirected_url, "search/*")
        self.assertIn(self.user_2.user.first_name,self.browser.find_element_by_class_name("main-content").text)

        # User sees an option to search for groups as well
        self.browser.find_element_by_class_name("side-pane").find_element_by_link_text("Groups").click()
        time.sleep(1)
        redirected_url = self.browser.current_url

        self.assertRegexpMatches(redirected_url, "search/*")
        self.assertIn(self.group_1.name,self.browser.find_element_by_class_name("main-content").text)

        # User sees a list with the results
        result_list = self.browser.find_element_by_class_name("group-search-results")
        results = result_list.find_elements_by_tag_name("li")
        self.assertEqual(len(results),4)
        image = results[0].find_element_by_css_selector("img.group-icon")
        group_link = results[0].find_element_by_css_selector("a.group-name")

        # In the first result, user will see an "add group icon"
        add_group_button = results[0].find_element_by_css_selector("a.btn-join-group i.material-icons")
        self.assertEqual(add_group_button.text,"group add")
        add_group_button.click()

        time.sleep(1)

        # Button will disappear
        add_group_button = results[0].find_elements_by_css_selector("a.btn-join-group i.material-icons")
        self.assertEqual(len(add_group_button),0)

        # User comes back to his home screen, sees the group in the group list
        self.browser.get(self.live_server_url)
        side_pane = self.browser.find_element_by_class_name('side-pane')
        group_list_wrapper = side_pane.find_element_by_id("group-list-wrapper")
        self.assertIn(self.group_1.name,group_list_wrapper.text)

    def test_search_group_buttons_show_up(self):
        # User access site and logs in
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User sees a search box
        form_search = self.browser.find_element_by_id('form_search')

        # User types in another user name
        form_search.find_element_by_css_selector("input[type='text']").send_keys(self.user_2.nickname)
        form_search.find_element_by_css_selector("input[type='text']").send_keys(Keys.ENTER)

        # User gets redirected to registration page, where he sees
        # the results of his search
        time.sleep(5)
        redirected_url = self.browser.current_url

        self.assertRegexpMatches(redirected_url, "search/*")
        self.assertIn(self.user_2.user.first_name,self.browser.find_element_by_class_name("main-content").text)

        # User sees an option to search for groups as well
        self.browser.find_element_by_class_name("side-pane").find_element_by_link_text("Groups").click()
        time.sleep(1)
        redirected_url = self.browser.current_url

        self.assertRegexpMatches(redirected_url, "search/*")

        # User sees a list with the results
        result_list = self.browser.find_element_by_class_name("group-search-results")
        results = result_list.find_elements_by_tag_name("li")
        for result in results:
            buttons = result.find_elements_by_css_selector("a.btn-join-group i.material-icons")
            disabled_buttons = result.find_elements_by_css_selector("a.btn-join-group.disabled i.material-icons")
            if self.group_3.name in result.text:
                self.assertEqual(len(buttons),0)
            elif self.group_4.name in result.text:
                self.assertEqual(len(disabled_buttons),1)
            else:
                self.assertEqual(len(buttons),1)
                # Handle the clicks for the first two buttons
                if self.group_1.name in result.text:
                    buttons[0].click()
                    time.sleep(1)
                    buttons = result.find_elements_by_css_selector("a.btn-join-group i.material-icons")
                    self.assertEqual(len(buttons),0)
                elif self.group_2.name in result.text:
                    buttons[0].click()
                    time.sleep(1)
                    buttons = result.find_elements_by_css_selector("a.disabled.btn-join-group i.material-icons")
                    self.assertEqual(len(buttons),1)

class GroupTest(StaticLiveServerTestCase):

    user_1 = None
    user_2 = None
    user_3 = None
    group_public = None
    group_private = None

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(2.5)

        # Create a user
        self.user_1 = PlayerFactory()
        self.user_1.user.set_password("123456")
        self.user_1.user.save()

        self.user_2 = PlayerFactory()
        self.user_2.user.set_password("123456")
        self.user_2.user.save()

        self.user_3 = PlayerFactory()
        self.user_3.user.set_password("123456")
        self.user_3.user.save()


        # Create groups
        self.group_public = self.user_1.create_group("Public Group",public = True)
        self.group_private = self.user_1.create_group("Private Group",public = False)

        self.group_1 = self.user_2.create_group("%s's Public Group" % (self.user_2.nickname),public=True)
        self.group_2 = self.user_2.create_group("%s's Private Group" % (self.user_2.nickname),public=False)
        self.group_3 = self.user_2.create_group("%s's Joined Group" % (self.user_2.nickname),public=True)
        self.group_4 = self.user_2.create_group("%s's Private Joined Group" % (self.user_2.nickname),public=False)
        self.group_5 = self.user_3.create_group("%s's Private Joined Group" % (self.user_3.nickname),public=False)
        self.user_1.join_group(self.group_3)
        self.user_1.join_group(self.group_4)
        self.user_3.join_group(self.group_2)
        self.user_3.join_group(self.group_4)
        self.user_1.join_group(self.group_5)

    def tearDown(self):
        self.browser.quit()

    def test_user_can_create_group(self):

        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User sees a plus button in the side pane, close to the group list
        side_pane = self.browser.find_element_by_class_name('side-pane')
        group_list_wrapper = side_pane.find_element_by_id("group-list-wrapper")
        add_group_button = group_list_wrapper.find_element_by_css_selector("a#btn-new-group i.material-icons")
        self.assertEqual(add_group_button.text,"add")
        add_group_button.click()

        # User clicks in create new group
        time.sleep(1)
        self.assertEqual(self.browser.current_url,"%s/group/create" % self.live_server_url)

        form_group_creation = self.browser.find_element_by_id("form-group-creation")

        # Fills the inputs
        form_group_creation.find_element_by_id("id_name").send_keys("Group Created")
        #form_group_creation.find_element_by_id("id_name").send_keys(keys.ENTER)

        form_group_creation.find_element_by_css_selector("input[type='submit']").click()
        time.sleep(1)

        # Gets redirected
        redirected_url = self.browser.current_url
        self.assertRegexpMatches(redirected_url, "group/\d+/")
        self.assertEqual("Group Created",self.browser.find_element_by_tag_name("h2").text)
        self.assertNotIn("Join",self.browser.find_element_by_class_name("side-pane").text)
        self.assertEqual(len(self.browser.find_element_by_id("member-list")
                                                    .find_elements_by_tag_name("li")),1)

    def test_user_can_join_public_group(self):

        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User enters the desired group url
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_public.id))

        # User clicks the join button
        side_pane = self.browser.find_element_by_class_name('side-pane')
        button = side_pane.find_element_by_css_selector("a.btn-join-group")
        self.assertIn("JOIN",button.text)
        button.click()
        time.sleep(5)
        # User now sees his name on the member list
        self.assertIn(self.user_2.user.first_name,self.browser.find_element_by_id("member-list").text)

    def test_join_button_behavior_on_group_page(self):

        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # First case, public group, not yet joined
        # Button shows up in page, then disappears
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_1.id))

        # User clicks the join button
        side_pane = self.browser.find_element_by_class_name('side-pane')
        button = side_pane.find_element_by_css_selector("a.btn-join-group")
        self.assertIn("JOIN",button.text)
        button.click()
        time.sleep(1)
        buttons = side_pane.find_elements_by_css_selector("a.btn-join-group")
        self.assertEqual(len(buttons),0)

        # Second case, private group, not yet joined
        # Button shows up and turns into a disabled button after click
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_2.id))

        side_pane = self.browser.find_element_by_class_name('side-pane')
        button = side_pane.find_element_by_css_selector("a.btn-join-group")
        self.assertIn("JOIN",button.text)
        button.click()
        time.sleep(1)

        button = side_pane.find_element_by_css_selector("a.btn-join-group.disabled")
        self.assertIn("MEMBERSHIP REQUESTED",button.text)

        # Third case, public group, joined (same behavior goes for private groups)
        # Button isn't present
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_3.id))

        # User clicks the join button
        side_pane = self.browser.find_element_by_class_name('side-pane')
        buttons = side_pane.find_elements_by_css_selector("a.btn-join-group")
        self.assertEqual(len(buttons),0)

        # Fourth case, private group, membership requested
        # Button disabled by default with message
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_4.id))
        side_pane = self.browser.find_element_by_class_name('side-pane')
        button = side_pane.find_element_by_css_selector("a.btn-join-group.disabled")
        self.assertIn("MEMBERSHIP REQUESTED",button.text)

    def test_admin_can_set_group_as_private(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User goes to group url
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_public.id))

        # In the side pane, user sees a checkbox with regarding group status
        side_pane = self.browser.find_element_by_class_name('side-pane')
        checkbox = side_pane.find_element_by_class_name("public-wrapper").find_element_by_tag_name("input")
        self.assertEqual(checkbox.is_enabled(),True)
        self.assertEqual(checkbox.get_attribute("checked"),"true")

        label = side_pane.find_element_by_class_name("public-wrapper").find_element_by_tag_name("label")
        label.click()


        # Reload group object
        time.sleep(1)
        group = Group.objects.get(pk=self.group_public.pk)
        self.assertEqual(group.public,False)

    def test_non_admin_cant_set_group_as_private(self):

        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User goes to group url
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_public.id))

        # In the side pane, user sees a checkbox with regarding group status
        side_pane = self.browser.find_element_by_class_name('side-pane')
        checkbox = side_pane.find_element_by_class_name("public-wrapper").find_element_by_tag_name("input")
        self.assertEqual(checkbox.is_enabled(),False)

        label = side_pane.find_element_by_class_name("public-wrapper").find_element_by_tag_name("label")
        label.click()
        time.sleep(1)

        # Reload group object
        group = Group.objects.get(pk=self.group_public.pk)
        self.assertEqual(group.public,True)

    def test_admin_can_accept_or_reject_membership_requests_in_homepage(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        requests_block = self.browser.find_element_by_class_name("membership-requests")
        membership_requests = requests_block.find_elements_by_tag_name("li")
        self.assertEqual(len(membership_requests),3)

        # Accept the first (user_1), reject the second (user_3)
        time.sleep(1)
        # self.assertEqual(membership_requests[0].find_element_by_class_name("player-name").text,self.user_1.get_name())
        if(str(self.user_1) == membership_requests[0].find_element_by_class_name("player-name").text):
            membership_requests[0].find_element_by_css_selector("a.btn-accept-group i.material-icons").click()
        else :
            membership_requests[0].find_element_by_css_selector("a.btn-reject-group i.material-icons").click()
        time.sleep(3)

        requests_block = self.browser.find_element_by_class_name("membership-requests")
        membership_requests = requests_block.find_elements_by_tag_name("li")
        self.assertEqual(len(membership_requests),2)
        if(str(self.user_1) == membership_requests[0].find_element_by_class_name("player-name").text):
            membership_requests[0].find_element_by_css_selector("a.btn-accept-group i.material-icons").click()
        else :
            membership_requests[0].find_element_by_css_selector("a.btn-reject-group i.material-icons").click()
        time.sleep(3)

        requests_block = self.browser.find_element_by_class_name("membership-requests")
        membership_requests = requests_block.find_elements_by_tag_name("li")
        self.assertEqual(len(membership_requests),1)

        if(str(self.user_1) == membership_requests[0].find_element_by_class_name("player-name").text):
            membership_requests[0].find_element_by_css_selector("a.btn-accept-group i.material-icons").click()
        else :
            membership_requests[0].find_element_by_css_selector("a.btn-reject-group i.material-icons").click()
        time.sleep(3)
        membership_requests = requests_block.find_elements_by_tag_name("li")
        self.assertEqual(len(membership_requests),0)

        self.browser.get("%s/group/%s" % (self.live_server_url,self.group_4.pk))

        self.assertIn(self.user_1.user.first_name,self.browser.find_element_by_id("member-list").text)
        self.assertNotIn(self.user_3.user.first_name,self.browser.find_element_by_id("member-list").text)

    def test_admin_can_accept_or_reject_membership_requests_in_group_page(self):
        self.browser.get(self.live_server_url)
        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%s" % (self.live_server_url,self.group_4.pk))

        requests_block = self.browser.find_element_by_class_name("membership-requests")
        membership_requests = requests_block.find_elements_by_tag_name("li")
        self.assertEqual(len(membership_requests),2)

        # Accept the first (user_1), reject the second (user_3)
        if(str(self.user_1) == membership_requests[0].find_element_by_class_name("player-name").text):
            membership_requests[0].find_element_by_css_selector("a.btn-accept-group i.material-icons").click()
        else :
            membership_requests[0].find_element_by_css_selector("a.btn-reject-group i.material-icons").click()

        time.sleep(3)
        self.assertIn(self.user_1.user.first_name,self.browser.find_element_by_id("member-list").text)

        requests_block = self.browser.find_element_by_class_name("membership-requests")
        membership_requests = requests_block.find_elements_by_tag_name("li")

        self.assertEqual(len(membership_requests),1)
        self.assertIn(self.user_1.user.first_name,self.browser.find_element_by_id("member-list").text)

        if(str(self.user_1) == membership_requests[0].find_element_by_class_name("player-name").text):
            membership_requests[0].find_element_by_css_selector("a.btn-accept-group i.material-icons").click()
        else :
            membership_requests[0].find_element_by_css_selector("a.btn-reject-group i.material-icons").click()
        time.sleep(3)

        requests_block = self.browser.find_element_by_class_name("membership-requests")
        membership_requests = requests_block.find_elements_by_tag_name("li")
        self.assertEqual(len(membership_requests),0)

        self.assertNotIn(self.user_3.user.first_name,self.browser.find_element_by_id("member-list").text)

    def test_non_admin_cant_see_membership_requests(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        requests_block = self.browser.find_elements_by_class_name("membership-requests")
        self.assertEqual(len(requests_block),0)

        self.browser.get("%s/group/%s" % (self.live_server_url,self.group_4.pk))

        requests_block = self.browser.find_elements_by_class_name("membership-requests")
        self.assertEqual(len(requests_block),0)

@override_settings(CELERY_ALWAYS_EAGER=True)
class MatchTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1.5)

        # Create a user
        self.user_1 = PlayerFactory()
        self.user_1.user.set_password("123456")
        self.user_1.user.save()

        self.user_2 = PlayerFactory()
        self.user_2.user.set_password("123456")
        self.user_2.user.save()

        # Create groups
        self.group_public = self.user_1.create_group("Public Group",public = True)
        self.group_private = self.user_1.create_group("Private Group",public = False)
        self.group_from_user_2 = self.user_2.create_group("User 2 Private Group",public = False)
        self.user_2.join_group(self.group_public)

    def tearDown(self):
        self.browser.quit()

    def test_user_schedule_match(self):

        # User 1 logs in
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User enters the desired group url
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_public.id))

        # User clicks "schedule match"
        self.browser.find_element_by_link_text("New Match").click()
        redirected_url = self.browser.current_url
        self.assertRegexpMatches(redirected_url, "group/\d+/match")

        # User fills the form with data on date, price, max and min people
        form_match = self.browser.find_element_by_id("form-group-match-creation")
        form_match.find_element_by_id("id_date").send_keys(datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
        form_match.find_element_by_id("id_price").send_keys("10")
        form_match.find_element_by_id("id_min_participants").send_keys("10")
        form_match.find_element_by_id("id_max_participants").send_keys("15")

        form_match.find_element_by_css_selector("input[type='submit']").click()
        time.sleep(2)
        # Check if user was redirected to match page
        redirected_url = self.browser.current_url
        self.assertRegexpMatches(redirected_url, "match/\d+/")

        # Check if an acceptance box is present
        buttons = self.browser.find_element_by_id("accept-wrapper").find_elements_by_tag_name("button")
        self.assertEqual(len(buttons),2)

        # Check if buttons are with the right labels
        self.assertEqual(buttons[0].text,"Yes")
        self.assertEqual(buttons[1].text,"No")

        # Return to the home page, then check if the schedule box is present and repeat button tests
        self.browser.get(self.live_server_url)

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")

        # User sees a table with a calendar
        calendar_view_rows = self.browser.find_element_by_id("schedule-box").find_elements_by_tag_name("tr")

        self.assertEqual(len(calendar_view_rows),2)

        # assert the columns
        self.assertEqual(len(calendar_view_rows[0].find_elements_by_tag_name("th")),7)
        self.assertEqual(len(calendar_view_rows[1].find_elements_by_tag_name("td")),7)

        # assert the days
        last_sunday = str((datetime.date.today()+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))).day)
        next_saturday = str((datetime.date.today()+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SA(+1))).day)
        self.assertIn("Sun",calendar_view_rows[0].find_elements_by_tag_name("th")[0].text)
        self.assertIn(last_sunday,calendar_view_rows[0].find_elements_by_tag_name("th")[0].text)
        self.assertIn("Sat",calendar_view_rows[0].find_elements_by_tag_name("th")[-1].text)
        self.assertIn(next_saturday,calendar_view_rows[0].find_elements_by_tag_name("th")[-1].text)

        self.assertEqual(len(match_invitations),1)

        # Check if an acceptance box is present
        button_container = match_invitations[0].find_element_by_class_name("confirm-container")

        # User sees two links inside them
        links = button_container.find_elements_by_tag_name("a")
        self.assertEqual(len(links),2)

        # Check if buttons are with the right labels
        self.assertEqual(links[0].find_element_by_tag_name("i").text,"done")
        self.assertEqual(links[1].find_element_by_tag_name("i").text,"clear")

        # Logs out
        self.browser.find_element_by_link_text("Logout").click()

        # User 2 logs in, sees the same match invitation
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")

        # User sees a table with a calendar
        calendar_view_rows = self.browser.find_element_by_id("schedule-box").find_elements_by_tag_name("tr")

        self.assertEqual(len(calendar_view_rows),2)

        # assert the columns
        self.assertEqual(len(calendar_view_rows[0].find_elements_by_tag_name("th")),7)
        self.assertEqual(len(calendar_view_rows[1].find_elements_by_tag_name("td")),7)

        # assert the days
        last_sunday = str((datetime.date.today()+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))).day)
        next_saturday = str((datetime.date.today()+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SA(+1))).day)
        self.assertIn("Sun",calendar_view_rows[0].find_elements_by_tag_name("th")[0].text)
        self.assertIn(last_sunday,calendar_view_rows[0].find_elements_by_tag_name("th")[0].text)
        self.assertIn("Sat",calendar_view_rows[0].find_elements_by_tag_name("th")[-1].text)
        self.assertIn(next_saturday,calendar_view_rows[0].find_elements_by_tag_name("th")[-1].text)

        self.assertEqual(len(match_invitations),1)

        # Check if an acceptance box is present
        button_container = match_invitations[0].find_element_by_class_name("confirm-container")

        # User sees two links inside them
        links = button_container.find_elements_by_tag_name("a")
        self.assertEqual(len(links),2)

        # Check if buttons are with the right labels
        self.assertEqual(links[0].find_element_by_tag_name("i").text,"done")
        self.assertEqual(links[1].find_element_by_tag_name("i").text,"clear")

    def test_manager_can_schedule_match_from_home_page(self):
        # User 1 logs in
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        buttons_match_create = self.browser.find_elements_by_class_name("btn-match-create")
        self.assertEqual(len(buttons_match_create),2)

        buttons_match_create[0].click()

        time.sleep(1)

        form_match = self.browser.find_element_by_id("form-group-match-creation")
        form_match.find_element_by_id("id_date").send_keys(datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
        form_match.find_element_by_id("id_price").send_keys("10")
        form_match.find_element_by_id("id_min_participants").send_keys("10")
        form_match.find_element_by_id("id_max_participants").send_keys("15")

        form_match.find_element_by_css_selector("input[type='submit']").click()

        time.sleep(1)

        self.browser.get(self.live_server_url)

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        self.assertEqual(len(match_invitations),1)

        # Logs out
        self.browser.find_element_by_link_text("Logout").click()

        # User 2 logs in, sees the same match invitation
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")

    def test_manager_can_schedule_match_from_group_page(self):

        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%s" % (self.live_server_url,self.group_public.pk))

        buttons_match_create = self.browser.find_elements_by_class_name("btn-match-create")
        self.assertEqual(len(buttons_match_create),1)

        buttons_match_create[0].click()

        time.sleep(1)

        form_match = self.browser.find_element_by_id("form-group-match-creation")
        form_match.find_element_by_id("id_date").send_keys(datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
        form_match.find_element_by_id("id_price").send_keys("10")
        form_match.find_element_by_id("id_min_participants").send_keys("10")
        form_match.find_element_by_id("id_max_participants").send_keys("15")

        form_match.find_element_by_css_selector("input[type='submit']").click()

        time.sleep(1)

        self.browser.get(self.live_server_url)

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        self.assertEqual(len(match_invitations),1)
        self.assertIn(self.group_public.name,match_invitations[0].text)

        # Logs out
        self.browser.find_element_by_link_text("Logout").click()

        # User 2 logs in, sees the same match invitation
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")

    def test_non_manager_cant_see_new_match_button(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%s" % (self.live_server_url,self.group_public.pk))

        buttons_match_create = self.browser.find_elements_by_class_name("btn-match-create")
        self.assertEqual(len(buttons_match_create),0)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_manager_can_schedule_until_end_of_month_or_year(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        buttons_match_create = self.browser.find_elements_by_class_name("btn-match-create")
        self.assertEqual(len(buttons_match_create),2)

        buttons_match_create[0].click()

        time.sleep(1)

        form_match = self.browser.find_element_by_id("form-group-match-creation")
        form_match.find_element_by_id("id_date").send_keys(datetime.date.today().strftime("%d/%m/%Y %H:%M"))
        form_match.find_element_by_id("id_price").send_keys("10")
        form_match.find_element_by_id("id_min_participants").send_keys("10")
        form_match.find_element_by_id("id_max_participants").send_keys("15")
        form_match.find_element_by_id("id_until_end_of_month")
        form_match.find_element_by_id("id_until_end_of_year")

        form_match.find_element_by_css_selector("input[type='submit']").click()

        time.sleep(1)

        # Perform the calendar tests


@override_settings(CELERY_ALWAYS_EAGER=True)
class CalendarTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1.5)

        # Create a user
        self.user_1 = PlayerFactory()
        self.user_1.user.set_password("123456")
        self.user_1.user.save()

        self.user_2 = PlayerFactory()
        self.user_2.user.set_password("123456")
        self.user_2.user.save()

        # Create groups
        self.group_public = self.user_1.create_group("Public Group",public = True)
        self.group_private = self.user_1.create_group("Private Group",public = False)
        self.user_2.join_group(self.group_public)

        self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(datetime.datetime.today()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0")
        )

        self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(datetime.datetime.today() + datetime.timedelta(days=7)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0")
        )

        self.user_1.schedule_match(self.group_private,
                                            date=timezone.make_aware(datetime.datetime.today()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0")
        )

    def tearDown(self):
        self.browser.quit()

    def test_calendar_navigation_weekly_on_home_page(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User sees a table with a calendar
        calendar_view_rows = self.browser.find_element_by_id("schedule-box").find_elements_by_tag_name("tr")

        self.assertEqual(len(calendar_view_rows),2)

        # assert the columns
        self.assertEqual(len(calendar_view_rows[0].find_elements_by_tag_name("th")),7)
        self.assertEqual(len(calendar_view_rows[1].find_elements_by_tag_name("td")),7)

        # assert the days
        last_sunday_date = datetime.date.today()+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))
        last_sunday = str((last_sunday_date).day)
        next_saturday = str((last_sunday_date+datetime.timedelta(days=6)).day)

        self.assertIn(last_sunday,calendar_view_rows[0].find_elements_by_tag_name("th")[0].text)
        self.assertIn(next_saturday,calendar_view_rows[0].find_elements_by_tag_name("th")[-1].text)

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        self.assertEqual(len(match_invitations),2)

        # User sees next button and clicks it
        self.browser.find_element_by_id("schedule-box").find_element_by_css_selector("a.btn-next i.material-icons").click()
        time.sleep(3)
        # assert the days for next week
        new_last_sunday = str((last_sunday_date+datetime.timedelta(days=7)).day)
        new_next_saturday = str((last_sunday_date+datetime.timedelta(days=7)+datetime.timedelta(days=6)).day)
        calendar_view_rows = self.browser.find_element_by_id("schedule-box").find_elements_by_tag_name("tr")

        self.assertIn(new_last_sunday,calendar_view_rows[0].find_elements_by_tag_name("th")[0].text)
        self.assertIn(new_next_saturday,calendar_view_rows[0].find_elements_by_tag_name("th")[-1].text)

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        self.assertEqual(len(match_invitations),1)

        # User sees prev button and clicks it
        self.browser.find_element_by_id("schedule-box").find_element_by_css_selector("a.btn-prev i.material-icons").click()
        time.sleep(3)
        last_sunday = str((last_sunday_date).day)
        next_saturday = str((last_sunday_date+datetime.timedelta(days=6)).day)

        calendar_view_rows = self.browser.find_element_by_id("schedule-box").find_elements_by_tag_name("tr")
        self.assertIn(last_sunday,calendar_view_rows[0].find_elements_by_tag_name("th")[0].text)
        self.assertIn(next_saturday,calendar_view_rows[0].find_elements_by_tag_name("th")[-1].text)

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        self.assertEqual(len(match_invitations),2)

        # User sees prev button and clicks it again
        self.browser.find_element_by_id("schedule-box").find_element_by_css_selector("a.btn-prev i.material-icons").click()
        time.sleep(3)
        last_sunday = str((last_sunday_date+datetime.timedelta(days=-7)).day)
        next_saturday = str((last_sunday_date+datetime.timedelta(days=-7)+datetime.timedelta(days=6)).day)

        calendar_view_rows = self.browser.find_element_by_id("schedule-box").find_elements_by_tag_name("tr")
        self.assertIn(last_sunday,calendar_view_rows[0].find_elements_by_tag_name("th")[0].text)
        self.assertIn(next_saturday,calendar_view_rows[0].find_elements_by_tag_name("th")[-1].text)

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        self.assertEqual(len(match_invitations),0)

    def test_calendar_display_monthly_on_group_page(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%s" % (self.live_server_url,self.group_public.pk))

        calendar_view = self.browser.find_element_by_id("calendar-monthly-view")

        # Assert headers
        header_cell_list = calendar_view.find_element_by_tag_name("thead").find_elements_by_tag_name("th")
        self.assertEqual(len(header_cell_list),7)
        self.assertIn("Sun",header_cell_list[0].text)
        self.assertIn("Sat",header_cell_list[-1].text)

        # Assert calendar rows
        today = datetime.date.today()
        first_day_of_month = datetime.date(today.year,today.month,1)
        sunday_before_first_day_of_month = first_day_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))
        last_date_of_month = datetime.date(today.year,today.month,1)+dateutil.relativedelta.relativedelta(months=1)
        next_saturday_after_last_date_of_month = last_date_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SA(1))

        calendar_row_list = calendar_view.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")

        self.assertEqual(len(calendar_row_list),((next_saturday_after_last_date_of_month-sunday_before_first_day_of_month).days+1)/7)
        match_invitations = self.browser.find_element_by_id("calendar-monthly-view").find_elements_by_class_name("match-invitation")


        self.assertEqual(len(match_invitations),MatchInvitation.objects.filter(
            match__group__pk=self.group_public.pk,
            player__pk=self.user_1.pk,
            match__date__gte=sunday_before_first_day_of_month,
            match__date__lte=next_saturday_after_last_date_of_month
        ).count())

    def test_calendar_navigation_monthly_on_group_page(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%s" % (self.live_server_url,self.group_public.pk))

        calendar_view = self.browser.find_element_by_id("calendar-monthly-view")

        # User sees next button and clicks it
        calendar_view.find_element_by_css_selector("a.btn-next i.material-icons").click()
        time.sleep(3)
        calendar_view = self.browser.find_element_by_id("calendar-monthly-view")

        # Assert days in next month
        header_cell_list = calendar_view.find_element_by_tag_name("thead").find_elements_by_tag_name("th")
        self.assertEqual(len(header_cell_list),7)
        self.assertIn("Sun",header_cell_list[0].text)
        self.assertIn("Sat",header_cell_list[-1].text)

        today_plus_one_month = datetime.date.today() + dateutil.relativedelta.relativedelta(months=1)
        first_day_of_month = datetime.date(today_plus_one_month.year,today_plus_one_month.month,1)
        sunday_before_first_day_of_month = first_day_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))
        last_date_of_month = datetime.date(today_plus_one_month.year,today_plus_one_month.month,1)+dateutil.relativedelta.relativedelta(months=1)
        next_saturday_after_last_date_of_month = last_date_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SA(1))

        calendar_row_list = calendar_view.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")

        self.assertEqual(len(calendar_row_list),((next_saturday_after_last_date_of_month-sunday_before_first_day_of_month).days+1)/7)

        self.assertIn(str(sunday_before_first_day_of_month.day),calendar_row_list[0].find_elements_by_tag_name("td")[0].text)
        self.assertIn(str(next_saturday_after_last_date_of_month.day),calendar_row_list[-1].find_elements_by_tag_name("td")[-1].text)

        # User clicks prev
        calendar_view.find_element_by_css_selector("a.btn-prev i.material-icons").click()
        time.sleep(3)
        calendar_view = self.browser.find_element_by_id("calendar-monthly-view")

        header_cell_list = calendar_view.find_element_by_tag_name("thead").find_elements_by_tag_name("th")
        self.assertEqual(len(header_cell_list),7)
        self.assertIn("Sun",header_cell_list[0].text)
        self.assertIn("Sat",header_cell_list[-1].text)

        today_plus_one_month = datetime.date.today()
        first_day_of_month = datetime.date(today_plus_one_month.year,today_plus_one_month.month,1)
        sunday_before_first_day_of_month = first_day_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))
        last_date_of_month = datetime.date(today_plus_one_month.year,today_plus_one_month.month,1)+dateutil.relativedelta.relativedelta(months=1)
        next_saturday_after_last_date_of_month = last_date_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SA(1))

        calendar_row_list = calendar_view.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")

        self.assertEqual(len(calendar_row_list),((next_saturday_after_last_date_of_month-sunday_before_first_day_of_month).days+1)/7)

        self.assertIn(str(sunday_before_first_day_of_month.day),calendar_row_list[0].find_elements_by_tag_name("td")[0].text)
        self.assertIn(str(next_saturday_after_last_date_of_month.day),calendar_row_list[-1].find_elements_by_tag_name("td")[-1].text)

        # User clicks prev again
        calendar_view.find_element_by_css_selector("a.btn-prev i.material-icons").click()
        time.sleep(3)
        calendar_view = self.browser.find_element_by_id("calendar-monthly-view")

        header_cell_list = calendar_view.find_element_by_tag_name("thead").find_elements_by_tag_name("th")
        self.assertEqual(len(header_cell_list),7)
        self.assertIn("Sun",header_cell_list[0].text)
        self.assertIn("Sat",header_cell_list[-1].text)

        today_plus_one_month = datetime.date.today() + dateutil.relativedelta.relativedelta(months=-1)
        first_day_of_month = datetime.date(today_plus_one_month.year,today_plus_one_month.month,1)
        sunday_before_first_day_of_month = first_day_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))
        last_date_of_month = datetime.date(today_plus_one_month.year,today_plus_one_month.month,1)+dateutil.relativedelta.relativedelta(months=1)
        next_saturday_after_last_date_of_month = last_date_of_month+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SA(1))

        calendar_row_list = calendar_view.find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")

        self.assertEqual(len(calendar_row_list),((next_saturday_after_last_date_of_month-sunday_before_first_day_of_month).days+1)/7)

        self.assertIn(str(sunday_before_first_day_of_month.day),calendar_row_list[0].find_elements_by_tag_name("td")[0].text)
        self.assertIn(str(next_saturday_after_last_date_of_month.day),calendar_row_list[-1].find_elements_by_tag_name("td")[-1].text)

@override_settings(CELERY_ALWAYS_EAGER=True)
class MatchConfirmationTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1.5)

        # Create a user
        self.user_1 = PlayerFactory()
        self.user_1.user.set_password("123456")
        self.user_1.user.save()

        self.user_2 = PlayerFactory()
        self.user_2.user.set_password("123456")
        self.user_2.user.save()

        last_sunday = datetime.datetime.today()+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))

        # Create groups
        self.group_public = self.user_1.create_group("Public Group",public = True)
        self.group_private = self.user_1.create_group("Private Group",public = False)
        self.user_2.join_group(self.group_public)

        self.match_sunday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0")
        )

        self.match_monday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday + datetime.timedelta(days=1)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0")
        )

        self.match_tuesday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday + datetime.timedelta(days=2)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0")
        )

        self.match_wednesday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday + datetime.timedelta(days=3)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0")
        )

        self.match_thursday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday + datetime.timedelta(days=4)),
                                            max_participants=0,
                                            min_participants=0,
                                            price=Decimal("20.0")
        )

        self.user_2.accept_match_invitation(match=self.match_sunday)
        self.user_2.refuse_match_invitation(match=self.match_monday)

    def tearDown(self):
        self.browser.quit()

    def test_match_confirmation_in_home_page(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")

        self.assertEqual(len(match_invitations),5)

        # Sunday match is confirmed
        sunday_match_invitation = match_invitations[0]
        buttons = sunday_match_invitation.find_element_by_class_name("confirm-container").find_elements_by_css_selector("a.disabled")
        self.assertEqual(len(buttons),1)
        self.assertIn("GOING",buttons[0].text)

        # Monday match is absence confirmed
        monday_match_invitation = match_invitations[1]
        buttons = monday_match_invitation.find_element_by_class_name("confirm-container").find_elements_by_css_selector("a.disabled")
        self.assertEqual(len(buttons),1)
        self.assertIn("NOT GOING",buttons[0].text)

        # Tuesday match is to be confirmed
        tuesday_match_invitation = match_invitations[-3]
        buttons = tuesday_match_invitation.find_element_by_class_name("confirm-container")

        # User sees two links inside them
        links = buttons.find_elements_by_tag_name("a")
        self.assertEqual(len(links),2)
        # Check if buttons are with the right labels
        self.assertEqual(links[0].find_element_by_tag_name("i").text,"done")
        self.assertEqual(links[1].find_element_by_tag_name("i").text,"clear")
        links[0].click()
        time.sleep(3)

        # Reload invitations
        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        tuesday_match_invitation = match_invitations[-3]
        buttons = tuesday_match_invitation.find_element_by_class_name("confirm-container").find_elements_by_css_selector("a.disabled")
        self.assertEqual(len(buttons),1)
        self.assertIn("GOING",buttons[0].text)

        time.sleep(1)
        # Wednesday match is to be absence confirmed
        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        wednesday_match_invitation = match_invitations[-2]
        buttons = wednesday_match_invitation.find_element_by_class_name("confirm-container")

        # User sees two links inside them
        links = buttons.find_elements_by_tag_name("a")
        self.assertEqual(len(links),2)
        # Check if buttons are with the right labels
        self.assertEqual(links[0].find_element_by_tag_name("i").text,"done")
        self.assertEqual(links[1].find_element_by_tag_name("i").text,"clear")
        links[1].click()
        time.sleep(3)

        # Reload invitations
        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        wednesday_match_invitation = match_invitations[-2]
        buttons = wednesday_match_invitation.find_element_by_class_name("confirm-container").find_elements_by_css_selector("a.disabled")
        self.assertEqual(len(buttons),1)
        self.assertIn("NOT GOING",buttons[0].text)

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        thursday_match_invitation = match_invitations[-1]
        buttons = thursday_match_invitation.find_element_by_class_name("confirm-container").find_elements_by_css_selector("a.disabled")
        self.assertEqual(len(buttons),1)
        self.assertIn("FULL",buttons[0].text)


        # Check the match pages
        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_sunday.pk))
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        self.assertIn(str(self.user_2),confirmed_list.text)

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_monday.pk))
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        self.assertNotIn(str(self.user_2),confirmed_list.text)

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_tuesday.pk))
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        self.assertIn(str(self.user_2),confirmed_list.text)

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_wednesday.pk))
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        self.assertNotIn(str(self.user_2),confirmed_list.text)

    def test_confirmed_list_in_match_page(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_sunday.pk))
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list")
        disabled_list = not_confirmed_list.find_elements_by_class_name("disabled")
        self.assertIn(str(self.user_2),confirmed_list.text)
        self.assertNotIn(str(self.user_2),not_confirmed_list.text)
        self.assertEqual(len(disabled_list),0)

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_monday.pk))
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list")
        disabled_list = not_confirmed_list.find_elements_by_class_name("disabled")
        self.assertNotIn(str(self.user_2),confirmed_list.text)
        self.assertIn(str(self.user_2)," ".join([x.text for x in disabled_list]))

    def test_match_confirmation_in_match_page(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_tuesday.pk))

        time.sleep(3)
        # User sees his name at the top of the list
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]
        self.assertIn(str(self.user_2),confirmed_first.text)
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list")
        self.assertNotIn(str(self.user_2),not_confirmed_list.text)

        # User sees the buttons beside his name
        button_container = confirmed_first.find_element_by_class_name("confirm-container")

        # User sees two links inside them
        links = button_container.find_elements_by_tag_name("a")
        self.assertEqual(len(links),2)

        # Check if buttons are with the right labels
        self.assertEqual(links[0].find_element_by_tag_name("i").text,"done")
        self.assertEqual(links[1].find_element_by_tag_name("i").text,"clear")

        links[0].click()
        time.sleep(3)

        # User is still at the confirmed list, but the buttons are gone
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        self.assertIn(str(self.user_2),confirmed_list.text)

        for row in confirmed_list.find_elements_by_tag_name("li"):
            if str(self.user_2) in row.text:
                    button_container = row.find_elements_by_class_name("confirm-container")
                    # User sees no links inside them
                    self.assertEqual(len(button_container),0)

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_wednesday.pk))

        time.sleep(3)
        # User sees his name at the top of the list
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]
        self.assertIn(str(self.user_2),confirmed_first.text)

        # User sees the buttons beside his name
        button_container = confirmed_first.find_element_by_class_name("confirm-container")

        # User sees two links inside them
        links = button_container.find_elements_by_tag_name("a")
        self.assertEqual(len(links),2)

        # Check if buttons are with the right labels
        self.assertEqual(links[0].find_element_by_tag_name("i").text,"done")
        self.assertEqual(links[1].find_element_by_tag_name("i").text,"clear")

        links[1].click()
        time.sleep(3)

        # User is still at the confirmed list, but the buttons are gone
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list")
        self.assertIn(str(self.user_2),not_confirmed_list.text)
        disabled_list = not_confirmed_list.find_elements_by_class_name("disabled")
        self.assertIn(str(self.user_2)," ".join([x.text for x in disabled_list]))

        self.assertNotIn(str(self.user_2),confirmed_list.text)

        for row in disabled_list:
            if str(self.user_2) in row.text:
                    button_container = row.find_elements_by_class_name("confirm-container")
                    # User sees no links inside them
                    self.assertEqual(len(button_container),0)

        # Now checks in the calendar in the home page
        self.browser.get(self.live_server_url)

        match_invitations = self.browser.find_element_by_id("schedule-box").find_elements_by_class_name("match-invitation")
        tuesday_match_invitation = match_invitations[-3]
        buttons = tuesday_match_invitation.find_element_by_class_name("confirm-container").find_elements_by_css_selector("a.disabled")
        self.assertEqual(len(buttons),1)
        self.assertIn("GOING",buttons[0].text)

        wednesday_match_invitation = match_invitations[-2]
        buttons = wednesday_match_invitation.find_element_by_class_name("confirm-container").find_elements_by_css_selector("a.disabled")
        self.assertEqual(len(buttons),1)
        self.assertIn("NOT GOING",buttons[0].text)

    """def test_user_can_set_automatic_confirmation_in_group(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        print(self.group_public.id)
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_public.id))
        time.sleep(2)
        self.browser.find_element_by_class_name("automatic-confirmation-wrapper").find_element_by_tag_name("label").click()
        time.sleep(2)
        self.browser.quit()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1.5)
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_public.id))
        time.sleep(5)

        checkbox = self.browser.find_element_by_class_name("automatic-confirmation-wrapper").find_element_by_tag_name("input")
        self.assertEqual(checkbox.is_selected(),True)

        self.browser.get(self.live_server_url)
        self.browser.find_element_by_link_text("Logout").click()

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_public.id))
        self.browser.find_element_by_link_text("New Match").click()

        # User fills the form with data on date, price, max and min people
        form_match = self.browser.find_element_by_id("form-group-match-creation")
        form_match.find_element_by_id("id_date").send_keys(datetime.date.today().strftime("%d/%m/%Y"))
        form_match.find_element_by_id("id_price").send_keys("10")
        form_match.find_element_by_id("id_min_participants").send_keys("10")
        form_match.find_element_by_id("id_max_participants").send_keys("15")

        form_match.find_element_by_css_selector("input[type='submit']").click()

        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        self.assertIn(str(self.user_2),confirmed_list.text)

    def test_admin_can_confirm_presence_of_any_user(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_public.id))
        self.browser.find_element_by_link_text("New Match").click()

        # User fills the form with data on date, price, max and min people
        form_match = self.browser.find_element_by_id("form-group-match-creation")
        form_match.find_element_by_id("id_date").send_keys(datetime.date.today().strftime("%d/%m/%Y"))
        form_match.find_element_by_id("id_price").send_keys("10")
        form_match.find_element_by_id("id_min_participants").send_keys("10")
        form_match.find_element_by_id("id_max_participants").send_keys("15")

        form_match.find_element_by_css_selector("input[type='submit']").click()
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list").find_elements_by_tag_name("li")
        for row in not_confirmed_list:
            if str(self.user_2) in row.text:
                links = row.find_elements_by_tag_name("a")
                self.assertEqual(len(links),2)

                # Check if buttons are with the right labels
                self.assertEqual(links[0].find_element_by_tag_name("i").text,"done")
                self.assertEqual(links[1].find_element_by_tag_name("i").text,"clear")

                links[0].click()
        time.sleep(1)
        confirmed_list = self.browser.find_elements_by_css_selector("li:not(.header)")
        self.assertNotIn(str(self.user_1),"".join([x.text for x in confirmed_list]))
        self.assertIn(str(self.user_2),"".join([x.text for x in confirmed_list]))
        for row in confirmed_list:
            if str(self.user_2) in row.text:
                links = row.find_elements_by_tag_name("a")
                self.assertEqual(len(links),0)
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list").find_elements_by_tag_name("li")
        header = self.browser.find_element_by_css_selector("li.header")
        self.assertIn(str(self.user_1),header.text)
        self.assertNotIn(str(self.user_2),"".join([x.text for x in not_confirmed_list]))

        # Refresh the page to see if nothing changed
        self.browser.refresh()
        confirmed_list = self.browser.find_elements_by_css_selector("li:not(.header)")
        self.assertNotIn(str(self.user_1),"".join([x.text for x in confirmed_list]))
        self.assertIn(str(self.user_2),"".join([x.text for x in confirmed_list]))
        for row in confirmed_list:
            if str(self.user_2) in row.text:
                links = row.find_elements_by_tag_name("a")
                self.assertEqual(len(links),0)
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list").find_elements_by_tag_name("li")
        header = self.browser.find_element_by_css_selector("li.header")
        self.assertIn(str(self.user_1),header.text)
        self.assertNotIn(str(self.user_2),"".join([x.text for x in not_confirmed_list]))"""

class VenueTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1.5)

        # Create a user
        self.user_1 = PlayerFactory()
        self.user_1.user.set_password("123456")
        self.user_1.user.save()

    def tearDown(self):
        self.browser.quit()

    def test_create_venue(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/venue/create" % (self.live_server_url,))

        self.browser.find_element_by_id("id_quadra").send_keys("Quadra")
        self.browser.find_element_by_class_name("geoposition-search").find_element_by_tag_name("input").send_keys("Rua do Teste")
        time.sleep(5)

        address = self.browser.find_element_by_class_name("geoposition-address").text

        self.browser.find_element_by_id("form-venue-creation").find_element_by_css_selector("input[type='submit']").click()
        time.sleep(3)

        redirected_url = self.browser.current_url
        self.assertRegexpMatches(redirected_url, "venue/\d+")

        self.assertIn(address,self.browser.find_element_by_class_name("venue-address").text)
