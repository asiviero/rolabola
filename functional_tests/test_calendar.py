from functional_tests import *

@override_settings(CELERY_ALWAYS_EAGER=True)
class CalendarTest(StaticLiveServerTestCase):

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

        # Create groups
        self.group_public = self.user_1.create_group("Public Group",public = True)
        self.group_private = self.user_1.create_group("Private Group",public = False)
        self.user_2.join_group(self.group_public)

        self.venue_1 = VenueFactory()

        self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(datetime.datetime.today()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1
        )

        self.user_1.schedule_match(self.group_public,
                                            date=timezone.make_aware(datetime.datetime.today() + datetime.timedelta(days=7)),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1
        )

        self.user_1.schedule_match(self.group_private,
                                            date=timezone.make_aware(datetime.datetime.today()),
                                            max_participants=15,
                                            min_participants=10,
                                            price=Decimal("20.0"),
                                            venue=self.venue_1
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
            match__date__gte=timezone.make_aware(datetime.datetime.combine(sunday_before_first_day_of_month,datetime.datetime.min.time())),
            match__date__lte=timezone.make_aware(datetime.datetime.combine(next_saturday_after_last_date_of_month,datetime.datetime.min.time())),
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
