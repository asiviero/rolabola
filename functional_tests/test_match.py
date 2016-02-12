from functional_tests import *

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
        buttons = self.browser.find_element_by_class_name("confirmed-list").find_element_by_class_name("header").find_element_by_class_name("confirm-container").find_elements_by_tag_name("a")
        self.assertEqual(len(buttons),2)

        # Check if buttons are with the right labels
        self.assertEqual(buttons[0].find_element_by_tag_name("i").text,"done")
        self.assertEqual(buttons[1].find_element_by_tag_name("i").text,"clear")

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

        time.sleep(3)

        buttons_match_create[0].click()

        time.sleep(3)

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

        time.sleep(3)

        buttons_match_create[0].click()

        time.sleep(3)

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

        self.venue_1 = VenueFactory()

        last_sunday = datetime.datetime.today()+dateutil.relativedelta.relativedelta(weekday=dateutil.relativedelta.SU(-1))

        # Create groups
        self.group_public = self.user_1.create_group("Public Group",public = True)
        self.group_private = self.user_1.create_group("Private Group",public = False)
        self.user_2.join_group(self.group_public)

        self.match_sunday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1
        )

        self.match_monday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday + datetime.timedelta(days=1)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1
        )

        self.match_tuesday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday + datetime.timedelta(days=2)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1
        )

        self.match_wednesday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday + datetime.timedelta(days=3)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1
        )

        self.match_thursday = self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(last_sunday + datetime.timedelta(days=4)),
                                            max_participants=0,
                                            min_participants=0,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1
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
        time.sleep(3)
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

    def test_admin_match_confirmation(self):
        self.browser.get(self.live_server_url)
        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_tuesday.pk))
        time.sleep(3)
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list")
        disabled_list = not_confirmed_list.find_elements_by_class_name("disabled")
        self.assertIn(str(self.user_1),confirmed_list.text)
        self.assertIn(str(self.user_2),not_confirmed_list.text)

        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]

        # Admin confirms his presence
        button_container = confirmed_first.find_element_by_class_name("confirm-container")
        links = button_container.find_elements_by_tag_name("a")
        self.assertEqual(len(links),2)

        links[0].click()
        time.sleep(3)

        # Refresh lists
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list")
        disabled_list = not_confirmed_list.find_elements_by_class_name("disabled")

        # Check user has no more buttons
        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]
        button_container = confirmed_first.find_elements_by_class_name("confirm-container")
        self.assertEqual(len(button_container),0)

        # Check non-confirmed remained with the buttons
        for row in not_confirmed_list.find_elements_by_tag_name("li"):
            button_container = row.find_element_by_class_name("confirm-container")
            links = button_container.find_elements_by_tag_name("a")
            self.assertEqual(len(links),2)

    def test_match_confirmation_revertion_on_match_page(self):
        # User logs in
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_tuesday.pk))
        time.sleep(3)

        # User accepts invitation to match 1
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]
        button_container = confirmed_first.find_element_by_class_name("confirm-container")

        links = button_container.find_elements_by_tag_name("a")
        links[0].click()
        time.sleep(3)

        # User sees his name in the confirmed list, along a button to cancel his confirmation
        # On the other users, he sees no button
        confirmed_list_li = self.browser.find_element_by_class_name("confirmed-list").find_elements_by_tag_name("li")
        refused_list_li = self.browser.find_element_by_class_name("not-confirmed-list").find_elements_by_class_name("disabled")

        for confirmed in confirmed_list_li:
            buttons = confirmed.find_element_by_class_name("revert-container")
            if str(self.user_2) in confirmed.text:
                links = buttons.find_elements_by_tag_name("a")
                self.assertEqual(len(links),1)
                self.assertEqual(links[0].text,"CANCEL")
            else:
                self.assertEqual(len(buttons),0)

        for refused in refused_list_li:
            buttons = confirmed.find_elements_by_class_name("revert-container")
            self.assertEqual(len(buttons),0)

        # User clicks the button to revert his confirmation
        for confirmed in confirmed_list_li:
            buttons = confirmed.find_elements_by_class_name("revert-container")
            if str(self.user_2) in confirmed.text:
                buttons[0].find_elements_by_tag_name("a")[0].click()
                time.sleep(3)

        # User sees his name on the top of the list again, without revertion button
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]
        self.assertIn(str(self.user_2),confirmed_first.text)
        buttons = confirmed_first.find_elements_by_class_name("revert-container")
        self.assertEqual(len(buttons),0)

        # User refuses invitation to match 2
        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_wednesday.pk))
        time.sleep(3)

        # User accepts invitation to match 1
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]
        button_container = confirmed_first.find_element_by_class_name("confirm-container")

        links = button_container.find_elements_by_tag_name("a")
        links[1].click()
        time.sleep(3)

        # User sees his name in the not-confirmed list, along a button to cancel his confirmation
        # On the other users, he sees no button
        confirmed_list_li = self.browser.find_element_by_class_name("confirmed-list").find_elements_by_tag_name("li")
        refused_list_li = self.browser.find_element_by_class_name("not-confirmed-list").find_elements_by_class_name("disabled")

        for confirmed in confirmed_list_li:
            buttons = confirmed.find_elements_by_class_name("revert-container")
            self.assertEqual(len(buttons),0)

        for refused in refused_list_li:
            buttons = refused.find_elements_by_class_name("revert-container")
            if str(self.user_2) in refused.text:
                self.assertEqual(len(buttons[0].find_elements_by_tag_name("a")),1)
            else:
                self.assertEqual(len(buttons),0)

        # User clicks the button
        for refused in refused_list_li:
            buttons = refused.find_elements_by_class_name("revert-container")
            if str(self.user_2) in refused.text:
                buttons[0].find_elements_by_tag_name("a")[0].click()
                time.sleep(3)

        # User sees his name on the top of the list again, without revertion button
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]
        self.assertIn(str(self.user_2),confirmed_first.text)
        buttons = confirmed_first.find_elements_by_class_name("revert-container")
        self.assertEqual(len(buttons),0)

    def test_admin_match_confirmation_revertion_on_match_page(self):
        # Admin logs in
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_tuesday.pk))
        time.sleep(3)

        # Admin accepts invitation to match 1
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]
        button_container = confirmed_first.find_element_by_class_name("confirm-container")

        links = button_container.find_elements_by_tag_name("a")
        links[0].click()
        time.sleep(3)

        # Admin confirms the other user as well
        non_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list").find_elements_by_tag_name("li")
        for non_confirmed in non_confirmed_list:
            if str(self.user_2) in non_confirmed.text:
                button_container = non_confirmed.find_element_by_class_name("confirm-container")
                links = button_container.find_elements_by_tag_name("a")
                links[0].click()
                time.sleep(3)

        # Admin sees his name in the confirmed list, along a button to cancel his confirmation
        # On the other users, he sees the button as well
        confirmed_list_li = self.browser.find_element_by_class_name("confirmed-list").find_elements_by_tag_name("li")
        self.assertEqual(len(confirmed_list_li),2)

        refused_list_li = self.browser.find_element_by_class_name("not-confirmed-list").find_elements_by_class_name("disabled")

        for confirmed in confirmed_list_li:
            buttons = confirmed.find_element_by_class_name("revert-container")
            links = buttons.find_elements_by_tag_name("a")
            self.assertEqual(len(links),1)
            self.assertEqual(links[0].text,"CANCEL")

        for refused in refused_list_li:
            buttons = confirmed.find_elements_by_class_name("revert-container")
            self.assertEqual(len(buttons),2)

        # Admin clicks the user button to revert his confirmation
        for confirmed in confirmed_list_li:
            buttons = confirmed.find_elements_by_class_name("revert-container")
            if str(self.user_2) in confirmed.text:
                buttons[0].find_elements_by_tag_name("a")[0].click()
                time.sleep(3)

        # Admin sees uuser name on the non-confirmed list again, without revertion button
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list")
        self.assertIn(str(self.user_2),not_confirmed_list.text)
        not_confirmed_list_li = not_confirmed_list.find_elements_by_tag_name("li")

        for not_confirmed in not_confirmed_list_li:
            if str(self.user_2) in not_confirmed.text:
                buttons = not_confirmed.find_elements_by_class_name("revert-container")
                self.assertEqual(len(buttons),0)

        # Admin refuses invitation to match 2
        self.browser.get("%s/group/%d/match/%d" % (self.live_server_url,self.group_public.id,self.match_wednesday.pk))
        time.sleep(3)

        # User accepts invitation to match 1
        confirmed_list = self.browser.find_element_by_class_name("confirmed-list")
        confirmed_first = confirmed_list.find_elements_by_tag_name("li")[0]
        button_container = confirmed_first.find_element_by_class_name("confirm-container")

        links = button_container.find_elements_by_tag_name("a")
        links[1].click()
        time.sleep(3)

        # Admin confirms absence of user
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list")
        # self.assertIn(str(self.user_2),not_confirmed_list.text)
        not_confirmed_list_li = not_confirmed_list.find_elements_by_tag_name("li")

        for non_confirmed in not_confirmed_list_li:
            if str(self.user_2) in non_confirmed.text:
                button_container = non_confirmed.find_element_by_class_name("confirm-container")
                links = button_container.find_elements_by_tag_name("a")
                links[1].click()
                time.sleep(3)
                break

        # Admin sees his name in the not-confirmed list, along a button to cancel his confirmation
        # On the other users, he sees the button as well
        confirmed_list_li = self.browser.find_element_by_class_name("confirmed-list").find_elements_by_tag_name("li")
        refused_list_li = self.browser.find_element_by_class_name("not-confirmed-list").find_elements_by_class_name("disabled")

        for refused in refused_list_li:
            buttons = refused.find_elements_by_class_name("revert-container")
            self.assertEqual(len(buttons[0].find_elements_by_tag_name("a")),1)

        # Admin clicks the user button
        for refused in refused_list_li:
            buttons = refused.find_elements_by_class_name("revert-container")
            if str(self.user_2) in refused.text:
                buttons[0].find_elements_by_tag_name("a")[0].click()
                time.sleep(3)
                break

        # Admin sees user name on not-confirmed list again, without revertion button
        not_confirmed_list = self.browser.find_element_by_class_name("not-confirmed-list")
        self.assertIn(str(self.user_2),not_confirmed_list.text)
        not_confirmed_list_li = not_confirmed_list.find_elements_by_tag_name("li")

        for not_confirmed in not_confirmed_list_li:
            if str(self.user_2) in not_confirmed.text:
                buttons = not_confirmed.find_elements_by_class_name("revert-container")
                self.assertEqual(len(buttons),0)
