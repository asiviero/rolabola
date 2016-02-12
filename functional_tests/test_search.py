from functional_tests import *

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

    def test_private_groups_are_marked(self):
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
        result_list = self.browser.find_element_by_class_name("group-search-results")
        results = result_list.find_elements_by_tag_name("li")
        for result in results:
            disabled_buttons = result.find_elements_by_css_selector("button.disabled")
            if self.group_1.name in result.text or self.group_3.name in result.text:
                self.assertEqual(len(disabled_buttons),0)
            elif self.group_2.name in result.text or self.group_4.name in result.text:
                self.assertEqual(len(disabled_buttons),1)
                self.assertIn("PRIVATE",disabled_buttons[0].text)

class SearchOrderTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1.5)

        self.user_1 = PlayerFactory()
        self.user_2 = PlayerFactory()
        self.user_3 = PlayerFactory()
        self.user_4 = PlayerFactory()
        self.user_5 = PlayerFactory()
        self.user_6 = PlayerFactory()
        self.user_7 = PlayerFactory()

        self.group_1 = self.user_1.create_group("Group 1", public=True)
        self.group_2 = self.user_1.create_group("Group 2", public=True)
        self.group_3 = self.user_1.create_group("Group 3", public=True)
        self.group_4 = self.user_4.create_group("Group 4", public=True)

        self.user_1.add_user(self.user_2)
        self.user_2.accept_request_from_friend(self.user_1)
        self.user_1.add_user(self.user_3)
        self.user_3.accept_request_from_friend(self.user_1)

        self.user_2.join_group(self.group_2)
        self.user_2.join_group(self.group_3)
        self.user_3.join_group(self.group_2)
        self.user_5.join_group(self.group_4)
        self.user_6.join_group(self.group_4)
        self.user_7.join_group(self.group_4)

    def tearDown(self):
        self.browser.quit()

    def test_search_results_group_order_by_friends_in_group(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User sees a search box
        form_search = self.browser.find_element_by_id('form_search')

        # User types in another user name
        form_search.find_element_by_css_selector("input[type='text']").send_keys("Group")
        form_search.find_element_by_css_selector("input[type='text']").send_keys(Keys.ENTER)

        # User gets redirected to registration page, where he sees
        # the results of his search
        time.sleep(1)
        redirected_url = self.browser.current_url

        # User sees an option to search for groups as well
        self.browser.find_element_by_class_name("side-pane").find_element_by_link_text("Groups").click()
        time.sleep(1)
        redirected_url = self.browser.current_url

        self.assertRegexpMatches(redirected_url, "search/*")

        # User sees a list with the results
        result_list = self.browser.find_element_by_class_name("group-search-results")
        results = result_list.find_elements_by_tag_name("li")
        self.assertIn(self.group_2.name,results[0].text)
        self.assertIn(self.group_3.name,results[1].text)
        self.assertIn(self.group_1.name,results[2].text)
        self.assertIn(self.group_4.name,results[3].text)

    def test_friends_in_groups_are_displayed(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        # User sees a search box
        form_search = self.browser.find_element_by_id('form_search')

        # User types in another user name
        form_search.find_element_by_css_selector("input[type='text']").send_keys("Group")
        form_search.find_element_by_css_selector("input[type='text']").send_keys(Keys.ENTER)

        # User gets redirected to registration page, where he sees
        # the results of his search
        time.sleep(1)
        redirected_url = self.browser.current_url

        # User sees an option to search for groups as well
        self.browser.find_element_by_class_name("side-pane").find_element_by_link_text("Groups").click()
        time.sleep(1)
        redirected_url = self.browser.current_url

        self.assertRegexpMatches(redirected_url, "search/*")

        # User sees a list with the results
        result_list = self.browser.find_element_by_class_name("group-search-results")
        results = result_list.find_elements_by_tag_name("li")
        for (key,result) in enumerate(results):
            if key == 0:
                self.assertEqual(len(result.find_element_by_class_name("friends-in-group-wrapper").find_elements_by_tag_name("img")),2)
            elif key == 1:
                self.assertEqual(len(result.find_element_by_class_name("friends-in-group-wrapper").find_elements_by_tag_name("img")),1)
            else:
                self.assertEqual(len(result.find_element_by_class_name("friends-in-group-wrapper").find_elements_by_tag_name("img")),0)
