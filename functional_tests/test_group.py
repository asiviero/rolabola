from functional_tests import *

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
        time.sleep(5)
        self.assertEqual(self.browser.current_url,"%s/group/create" % self.live_server_url)

        form_group_creation = self.browser.find_element_by_id("form-group-creation")

        # Fills the inputs
        form_group_creation.find_element_by_id("id_name").send_keys("Group Created")
        #form_group_creation.find_element_by_id("id_name").send_keys(keys.ENTER)

        form_group_creation.find_element_by_css_selector("input[type='submit']").click()
        time.sleep(5)

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
        time.sleep(5)
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
        time.sleep(5)
        buttons = side_pane.find_elements_by_css_selector("a.btn-join-group")
        self.assertEqual(len(buttons),0)

        # Second case, private group, not yet joined
        # Button shows up and turns into a disabled button after click
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_2.id))

        side_pane = self.browser.find_element_by_class_name('side-pane')
        button = side_pane.find_element_by_css_selector("a.btn-join-group")
        self.assertIn("JOIN",button.text)
        button.click()
        time.sleep(5)

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
        time.sleep(5)
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
        time.sleep(5)
        # In the side pane, user sees a checkbox with regarding group status
        side_pane = self.browser.find_element_by_class_name('side-pane')
        checkbox = side_pane.find_element_by_class_name("public-wrapper").find_element_by_tag_name("input")
        self.assertEqual(checkbox.is_enabled(),False)

        label = side_pane.find_element_by_class_name("public-wrapper").find_element_by_tag_name("label")
        label.click()
        time.sleep(5)

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
        time.sleep(5)
        # self.assertEqual(membership_requests[0].find_element_by_class_name("player-name").text,self.user_1.get_name())
        if(str(self.user_1) == membership_requests[0].find_element_by_class_name("player-name").text):
            membership_requests[0].find_element_by_css_selector("a.btn-accept-group i.material-icons").click()
        else :
            membership_requests[0].find_element_by_css_selector("a.btn-reject-group i.material-icons").click()
        time.sleep(5)

        requests_block = self.browser.find_element_by_class_name("membership-requests")
        membership_requests = requests_block.find_elements_by_tag_name("li")
        self.assertEqual(len(membership_requests),2)
        if(str(self.user_1) == membership_requests[0].find_element_by_class_name("player-name").text):
            membership_requests[0].find_element_by_css_selector("a.btn-accept-group i.material-icons").click()
        else :
            membership_requests[0].find_element_by_css_selector("a.btn-reject-group i.material-icons").click()
        time.sleep(5)

        requests_block = self.browser.find_element_by_class_name("membership-requests")
        membership_requests = requests_block.find_elements_by_tag_name("li")
        self.assertEqual(len(membership_requests),1)

        if(str(self.user_1) == membership_requests[0].find_element_by_class_name("player-name").text):
            membership_requests[0].find_element_by_css_selector("a.btn-accept-group i.material-icons").click()
        else :
            membership_requests[0].find_element_by_css_selector("a.btn-reject-group i.material-icons").click()
        time.sleep(5)
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

        time.sleep(5)
        self.assertIn(self.user_1.user.first_name,self.browser.find_element_by_id("member-list").text)

        requests_block = self.browser.find_element_by_class_name("membership-requests")
        membership_requests = requests_block.find_elements_by_tag_name("li")

        self.assertEqual(len(membership_requests),1)
        self.assertIn(self.user_1.user.first_name,self.browser.find_element_by_id("member-list").text)

        if(str(self.user_1) == membership_requests[0].find_element_by_class_name("player-name").text):
            membership_requests[0].find_element_by_css_selector("a.btn-accept-group i.material-icons").click()
        else :
            membership_requests[0].find_element_by_css_selector("a.btn-reject-group i.material-icons").click()
        time.sleep(5)

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
    def test_match_selection_on_group_page(self):
        # This test should check if the next match scheduled for a group is selected
        # when the group page is accessed. On the right side of it, a map with this
        # match's location, map and date/time.
        #def schedule_match(self,group,date,max_participants,min_participants,price,venue,until=None):

        venue_1 = VenueFactory()
        venue_2 = VenueFactory()

        tomorrow = timezone.make_aware(datetime.datetime.today() + datetime.timedelta(days = 1))
        after_tomorrow = timezone.make_aware(datetime.datetime.today() + datetime.timedelta(days = 2))
        yesterday = timezone.make_aware(datetime.datetime.today() - datetime.timedelta(days = 1))

        match_tomorrow = self.user_1.schedule_match(
            group = self.group_public,
            date = tomorrow,
            max_participants = 15,
            min_participants = 10,
            price = 10,
            venue = venue_1
        )
        match_after_tomorrow = self.user_1.schedule_match(
            group = self.group_public,
            date = after_tomorrow,
            max_participants = 15,
            min_participants = 10,
            price = 10,
            venue = venue_2
        )
        match_yesterday = self.user_1.schedule_match(
            group = self.group_public,
            date = yesterday,
            max_participants = 15,
            min_participants = 10,
            price = 10,
            venue = venue_2
        )

        # User 1 logs in
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%s" % (self.live_server_url,self.group_public.pk))

        # Check for the info in the side bar
        map_wrapper = self.browser.find_element_by_id("group-map-wrapper")
        map_div = map_wrapper.find_element_by_id("map-canvas")
        location_address_label = map_wrapper.find_element_by_class_name("match-location-address")
        self.assertEqual(location_address_label.text, match_tomorrow.venue.address.replace("\n"," "))
        time_label = map_wrapper.find_element_by_class_name("match-time")
        self.assertEqual(time_label.text, match_tomorrow.date.strftime("%H:%M"))

        calendar_table = self.browser.find_element_by_class_name("calendar-table")
        calendar_table_td_list = calendar_table.find_elements_by_tag_name("td")

        for cell in calendar_table_td_list:
            # inactive = cell.find_elements_by_class_name("inactive")
            label = cell.find_element_by_tag_name("label")
            if "inactive" in label.get_attribute("class"):
                continue
            if str(label.text) == str(tomorrow.day):
                # Get the first match in the list and checks if its labeled as active
                match_invitations = cell.find_elements_by_class_name("match-invitation")
                self.assertIn(" active",match_invitations[0].get_attribute("class"))
            if str(label.text) == str(after_tomorrow.day):
                # Clicks on the other
                cell.find_elements_by_class_name("match-invitation")[0].find_element_by_class_name("time").click()
                # cell.click()
                time.sleep(1)
                match_invitations = cell.find_elements_by_class_name("match-invitation")
                self.assertNotIn("inactive",match_invitations[0].get_attribute("class"))
                self.assertIn(" active",match_invitations[0].get_attribute("class"))
                # Check for the info in the side bar
                map_wrapper = self.browser.find_element_by_id("group-map-wrapper")
                map_div = map_wrapper.find_element_by_id("map-canvas")
                location_address_label = map_wrapper.find_element_by_class_name("match-location-address")
                self.assertEqual(location_address_label.text, match_after_tomorrow.venue.address.replace("\n"," "))
                time_label = map_wrapper.find_element_by_class_name("match-time")
                self.assertEqual(time_label.text, match_after_tomorrow.date.strftime("%H:%M"))
