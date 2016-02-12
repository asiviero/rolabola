from functional_tests import *

class VenueTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)

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
        time.sleep(5)

        redirected_url = self.browser.current_url
        self.assertRegexpMatches(redirected_url, "venue/\d+")

        self.assertIn(address,self.browser.find_element_by_class_name("venue-address").text)
