from functional_tests import *

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
