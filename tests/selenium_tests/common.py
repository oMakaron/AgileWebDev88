from unittest import TestCase
from multiprocessing import Process

from selenium.webdriver import Firefox, FirefoxOptions

from app import create_app, db
from app.models import User, Chart
from config import TestConfig


LOCAL_HOST = "http://127.0.0.1:5000"

def make_path(*elements: str) -> str:
    return '/'.join([LOCAL_HOST, *elements])


class TestBase(TestCase):

    def goto(self, *path) -> None:
        self.driver.get(make_path(*path))

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

    def tearDown(self) -> None:
        self.driver.close()

        self.server.terminate()

        db.session.remove()
        db.drop_all()

        self.app_context.pop()

    @staticmethod
    def create_user(full_name, email, password):
        user = User(fullname=full_name, email=email) # type: ignore
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def create_chart(name, owner, file, spec):
        chart = Chart(name=name, owner_id=owner, file_id=file, spec=spec) # type: ignore
        db.session.add(chart)
        db.session.commit()
        return chart

