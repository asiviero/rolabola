from functional_tests import *
import sys

class MessageTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)

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
        self.user_4 = PlayerFactory()
        self.user_4.user.set_password("123456")
        self.user_4.user.save()
        self.group_1 = self.user_1.create_group("Group 1", public=True)
        self.group_2 = self.user_1.create_group("Group 2", public=False)
        self.user_2.join_group(self.group_1)
        self.user_2.join_group(self.group_2)
        self.user_1.accept_request_group(group=self.group_2,user=self.user_2)
        self.user_3.join_group(self.group_1)
        self.user_3.join_group(self.group_2)
        self.group_3 = self.user_2.create_group("Group 3", public=True)

        # Message sending
        self.user_1.send_message_group(group=self.group_1,message="test message 1")
        self.user_2.send_message_group(group=self.group_1,message="test message 2")
        self.user_3.send_message_group(group=self.group_1,message="test message 3")
        self.user_1.send_message_group(group=self.group_2,message="test message 1")
        self.user_2.send_message_group(group=self.group_2,message="test message 2")
        self.user_3.send_message_group(group=self.group_2,message="test message 3")

    def tearDown(self):
        self.browser.quit()

    def test_user_can_post_message_to_group_wall(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_1.id))

        # User sees the message wall
        message_wall = self.browser.find_element_by_id("message-wall")

        # User sees the 3 messages
        messages = message_wall.find_elements_by_class_name("message-wrapper")
        self.assertEqual(len(messages),3)

        # In each of those, user sees a picture, a name and a message
        for message in messages:
            self.assertEqual(len(message.find_elements_by_class_name("message-author-img")),1)
            self.assertEqual(len(message.find_elements_by_class_name("message-author-name")),1)
            self.assertEqual(len(message.find_elements_by_class_name("message-text")),1)

        # User sees the form below the wall
        message_form = message_wall.find_element_by_tag_name("form")

        message_form.find_element_by_id("id_message").send_keys("Message sent")
        message_form.find_element_by_id("id_message").send_keys(Keys.ENTER)

        time.sleep(3)

        # User now sees his message atop
        message_wall = self.browser.find_element_by_id("message-wall")

        # User sees the 3 messages
        messages = message_wall.find_elements_by_class_name("message-wrapper")
        self.assertEqual(len(messages),4)
        self.assertEqual(messages[0].find_element_by_class_name("message-text").text,"Message sent")

        # Updates the page, check if it is still there
        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_1.id))

        # User sees the message wall
        message_wall = self.browser.find_element_by_id("message-wall")

        # User sees the 3 messages
        messages = message_wall.find_elements_by_class_name("message-wrapper")
        self.assertEqual(len(messages),4)
        self.assertEqual(messages[0].find_element_by_class_name("message-text").text,"Message sent")

    def test_user_can_delete_own_messages(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_2.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_1.id))

        # User sees the message wall
        message_wall = self.browser.find_element_by_id("message-wall")

        # User sees the 3 messages
        messages = message_wall.find_elements_by_class_name("message-wrapper")

        self.assertEqual(len(messages[0].find_elements_by_class_name("btn-delete-message")),0)
        self.assertEqual(len(messages[1].find_elements_by_class_name("btn-delete-message")),1)
        self.assertEqual(len(messages[2].find_elements_by_class_name("btn-delete-message")),0)

        # User clicks the delete button
        messages[1].find_element_by_class_name("btn-delete-message").click()
        time.sleep(1)

        # Message disappears
        messages = message_wall.find_elements_by_class_name("message-wrapper")
        self.assertEqual(len(messages),2)
        self.assertEqual(len(messages[0].find_elements_by_class_name("btn-delete-message")),0)
        self.assertEqual(len(messages[1].find_elements_by_class_name("btn-delete-message")),0)
        self.assertEqual(messages[0].find_element_by_class_name("message-text").text,"test message 3")
        self.assertEqual(messages[1].find_element_by_class_name("message-text").text,"test message 1")

        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_1.id))
        message_wall = self.browser.find_element_by_id("message-wall")
        messages = message_wall.find_elements_by_class_name("message-wrapper")
        self.assertEqual(len(messages),2)
        self.assertEqual(len(messages[0].find_elements_by_class_name("btn-delete-message")),0)
        self.assertEqual(len(messages[1].find_elements_by_class_name("btn-delete-message")),0)
        self.assertEqual(messages[0].find_element_by_class_name("message-text").text,"test message 3")
        self.assertEqual(messages[1].find_element_by_class_name("message-text").text,"test message 1")

    def test_admin_can_delete_any_message(self):
        self.browser.get(self.live_server_url)

        form_login = self.browser.find_element_by_id('form_login')
        form_login.find_element_by_id("id_username").send_keys(self.user_1.user.username)
        form_login.find_element_by_id("id_password").send_keys("123456")
        form_login.find_element_by_css_selector("input[type='submit']").click()

        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_1.id))

        # User sees the message wall
        message_wall = self.browser.find_element_by_id("message-wall")

        # User sees the 3 messages
        messages = message_wall.find_elements_by_class_name("message-wrapper")

        self.assertEqual(len(messages[0].find_elements_by_class_name("btn-delete-message")),1)
        self.assertEqual(len(messages[1].find_elements_by_class_name("btn-delete-message")),1)
        self.assertEqual(len(messages[2].find_elements_by_class_name("btn-delete-message")),1)

        # User clicks the delete button
        messages[1].find_element_by_class_name("btn-delete-message").click()
        time.sleep(1)
        # Message disappears
        messages = self.browser.find_element_by_id("message-wall").find_elements_by_class_name("message-wrapper")

        self.assertEqual(len(messages),2)
        self.assertEqual(len(messages[0].find_elements_by_class_name("btn-delete-message")),1)
        self.assertEqual(len(messages[1].find_elements_by_class_name("btn-delete-message")),1)
        self.assertEqual(messages[0].find_element_by_class_name("message-text").text,"test message 3")
        self.assertEqual(messages[1].find_element_by_class_name("message-text").text,"test message 1")

        self.browser.get("%s/group/%d/" % (self.live_server_url,self.group_1.id))
        message_wall = self.browser.find_element_by_id("message-wall")
        messages = message_wall.find_elements_by_class_name("message-wrapper")
        self.assertEqual(len(messages),2)
        self.assertEqual(len(messages[0].find_elements_by_class_name("btn-delete-message")),1)
        self.assertEqual(len(messages[1].find_elements_by_class_name("btn-delete-message")),1)
        self.assertEqual(messages[0].find_element_by_class_name("message-text").text,"test message 3")
        self.assertEqual(messages[1].find_element_by_class_name("message-text").text,"test message 1")
