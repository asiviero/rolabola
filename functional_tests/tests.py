from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase, RequestFactory
from django.contrib.auth import authenticate

from social_list.factories import *
import time

class NewVisitorTest(LiveServerTestCase):

    user_1 = None
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(0.5)

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
        form_registration.find_element_by_id("id_username").send_keys("username")
        form_registration.find_element_by_id("id_first_name").send_keys("First Name")
        form_registration.find_element_by_id("id_last_name").send_keys("Last Name")
        form_registration.find_element_by_id("id_email").send_keys("email@email.com")
        form_registration.find_element_by_id("id_password1").send_keys("123456")
        form_registration.find_element_by_id("id_password2").send_keys("123456")

        # User hits the submit button and waits for success
        form_registration.find_element_by_css_selector("input[type='submit']").click()

        time.sleep(1)
        redirected_url = self.browser.current_url
        self.assertEqual(redirected_url,self.live_server_url + "/")

        # User sees his first name and nickname on screen
        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Hi, First Name (Nickname)", page_text)



    def test_login(self):

        # Existing user access the website, sees login and registration form
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_registration = self.browser.find_element_by_id('form_registration')

        # User fills his login info
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")

        # User hits the submit button and waits for success
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User sees his first name and nickname on screen
        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertIn("Hi, %s (%s)" % (self.user_1.user.first_name, self.user_1.nickname), page_text)
        time.sleep(1)


    def test_logout(self):

        # Existing user access the website, sees login and registration form
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_registration = self.browser.find_element_by_id('form_registration')

        # User fills his login info
        # User fills his login info
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
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

class SearchTest(LiveServerTestCase):

    user_1 = None
    user_2 = None
    group_1 = None

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(0.5)

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
        self.group_1 = GroupFactory()
        self.group_1.name = "%s's Group" % (self.user_2.nickname)
        self.group_1.save()

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

class UserAddTest(self):
    pass
