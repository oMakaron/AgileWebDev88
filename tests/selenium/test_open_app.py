from unittest import TestCase
from multiprocessing import Process
from time import sleep

from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Expect

from app import create_app, db
from app.models import User
from config import TestConfig


LOCAL_HOST = 'http://127.0.0.1:5000'


class TestSignup(TestCase):

    def setUp(self) -> None:
        app = create_app(TestConfig)
        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()

        self.server = Process(target=app.run)
        self.server.start()

        options = FirefoxOptions()
        # options.add_argument("--headless")
        self.driver = Firefox(options=options)

    @staticmethod
    def create_user(full_name, email, password):
        user = User(fullname=full_name, email=email) # type: ignore
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def make_path(*path) -> str:
        return '/'.join([LOCAL_HOST, *path])

    def goto(self, *path) -> None:
        self.driver.get(TestSignup.make_path(*path))

    def test_signup(self) -> None:
        self.driver.get(LOCAL_HOST)

        self.driver.find_element(By.ID, "signup").click()

        WebDriverWait(self.driver, 10).until(Expect.visibility_of_element_located((By.ID, "name")))

        self.driver.find_element(By.ID, "name").send_keys("John Tableman")
        self.driver.find_element(By.ID, "email").send_keys("john@tables.com")
        self.driver.find_element(By.ID, "password").send_keys("asdflkjh")
        self.driver.find_element(By.ID, "confirm").send_keys("asdflkjh")
        self.driver.find_element(By.ID, "submit").click()

        WebDriverWait(self.driver, 10).until(Expect.url_to_be(TestSignup.make_path("login")))

        user = db.session.query(User).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("asdflkjh")) # type: ignore
        self.assertEqual("John Tableman", user.fullname) # type: ignore
        self.assertEqual("john@tables.com", user.email) # type: ignore


    def test_login(self) -> None:
        user = TestSignup.create_user('John Tableman', 'john@tables.com', 'asdflkjh')

        self.goto("login")

        self.driver.find_element(By.ID, "email").send_keys("john@tables.com")
        self.driver.find_element(By.ID, "password").send_keys("asdflkjh")
        self.driver.find_element(By.ID, "submit").click()

        WebDriverWait(self.driver, 10).until_not(Expect.url_to_be(TestSignup.make_path('login')))

        self.assertEqual(TestSignup.make_path('dashboard'), self.driver.current_url)


    def tearDown(self) -> None:
        self.driver.close()

        self.server.terminate()

        db.session.remove()
        db.drop_all()

        self.app_context.pop()
