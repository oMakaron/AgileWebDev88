from os import remove
from csv import writer
from tempfile import NamedTemporaryFile

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as Expect

from app import db
from app.models import Chart
from common import TestBase, make_path


class TestSignup(TestBase):

    def setUp(self) -> None:
        # Do normal setup
        super().setUp()

        try:
            # Create a logged in user
            self.user = self.create_user('John Tableman', 'john@tables.com', 'asdflkjh')

            self.goto('login')

            self.driver.find_element(By.ID, "email").send_keys("john@tables.com")
            self.driver.find_element(By.ID, "password").send_keys("asdflkjh")
            self.driver.find_element(By.ID, "submit").click()

        except Exception:
            self.tearDown()
            raise Exception('Failed to setup test.')


    def test_create_valid_chart(self) -> None:
        self.goto('dashboard')

        self.driver.find_element(By.ID, "addChartBtn").click()
        WebDriverWait(self.driver, 10).until(Expect.url_to_be(make_path('generate-graph')))


        with NamedTemporaryFile(mode='w', newline='', delete=False, suffix='.csv') as temp:
            file_writter = writer(temp)
            file_writter.writerows([
                ['header 1', 'header 2', 'header 3'],
                ['1',        '2',        '3'       ],
                ['4',        '5',        '6'       ]
            ])
            path = temp.name

        try:
            self.driver.find_element(By.ID, "up-file").send_keys(path)
            self.driver.find_element(By.ID, "up-submit_upload").click()

            Select(self.driver.find_element(By.ID, "ch-graph_type")).select_by_value("line")
            Select(self.driver.find_element(By.ID, "ch-x_col")).select_by_value("header 1")
            Select(self.driver.find_element(By.ID, "ch-y_col")).select_by_value("header 3")

            self.driver.find_element(By.ID, "ch-submit_generate").click()

        finally:
            remove(path)

        self.assertIsNone(db.session.query(Chart).first())

