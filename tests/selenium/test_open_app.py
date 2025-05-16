from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Expect

from app import db
from app.models import User

from common import TestBase, make_path, LOCAL_HOST


class TestSignup(TestBase):

    def test_signup(self) -> None:
        self.driver.get(LOCAL_HOST)

        self.driver.find_element(By.ID, "signup").click()

        WebDriverWait(self.driver, 10).until(Expect.visibility_of_element_located((By.ID, "name")))

        self.driver.find_element(By.ID, "name").send_keys("John Tableman")
        self.driver.find_element(By.ID, "email").send_keys("john@tables.com")
        self.driver.find_element(By.ID, "password").send_keys("asdflkjh")
        self.driver.find_element(By.ID, "confirm").send_keys("asdflkjh")
        self.driver.find_element(By.ID, "submit").click()

        WebDriverWait(self.driver, 10).until(Expect.url_to_be(make_path("login")))

        user = db.session.query(User).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("asdflkjh")) # type: ignore
        self.assertEqual("John Tableman", user.fullname) # type: ignore
        self.assertEqual("john@tables.com", user.email) # type: ignore


    def test_login(self) -> None:
        TestSignup.create_user('John Tableman', 'john@tables.com', 'asdflkjh')

        self.goto("login")

        self.driver.find_element(By.ID, "email").send_keys("john@tables.com")
        self.driver.find_element(By.ID, "password").send_keys("asdflkjh")
        self.driver.find_element(By.ID, "submit").click()

        WebDriverWait(self.driver, 10).until_not(Expect.url_to_be(make_path('login')))

        self.assertEqual(make_path('dashboard'), self.driver.current_url)

