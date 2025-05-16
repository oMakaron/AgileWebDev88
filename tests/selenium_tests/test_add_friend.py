from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Expect

from app import db
from app.models import User, Friendship
from common import TestBase, make_path


class TestAddFriend(TestBase):

    def setUp(self):
        super().setUp()

        # Create two users: the logged-in user and the friend
        self.user = self.create_user('Alice Example', 'alice@example.com', 'alicepw')
        self.friend = self.create_user('Bob Example',   'bob@example.com',   'bobpw')

        # Log in as Alice
        self.goto('login')
        self.driver.find_element(By.ID, "email").send_keys(self.user.email)
        self.driver.find_element(By.ID, "password").send_keys('alicepw')
        self.driver.find_element(By.ID, "submit").click()
        WebDriverWait(self.driver, 10).until(
            Expect.url_to_be(make_path('dashboard'))
        )

    def test_add_friend(self):
        # Navigate to "Add Friend"
        self.goto('dashboard')
        self.driver.find_element(By.ID, "addFriendBtn").click()
        WebDriverWait(self.driver, 10).until(
            Expect.url_to_be(make_path('add-friend'))
        )

        # Fill in Bob's email and submit
        self.driver.find_element(By.ID, "friend_email").send_keys(self.friend.email)
        self.driver.find_element(By.ID, "submit_add_friend").click()

        # Wait for Bob to appear in the friends list
        WebDriverWait(self.driver, 10).until(
            Expect.visibility_of_element_located((By.CSS_SELECTOR, ".friend-item"))
        )

        # Verify in the database
        relation = Friendship.query.filter_by(
            user_id=self.user.id,
            friend_id=self.friend.id
        ).first()
        self.assertIsNotNone(relation)
