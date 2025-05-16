import os
from csv import writer
from tempfile import NamedTemporaryFile

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as Expect

from app import db
from app.models import User, ChatMessage, Chart, File
from common import TestBase, make_path


class TestShareData(TestBase):

    def setUp(self):
        super().setUp()

        # Create two users: the sharer and the recipient
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

    def tearDown(self):
        super().tearDown()

    def test_share_chart_with_friend(self):
        # 1) Upload a CSV and generate a chart
        with NamedTemporaryFile(mode='w', newline='', delete=False, suffix='.csv') as tmp:
            file_writer = writer(tmp)
            file_writer.writerows([
                ['X','Y'],
                ['1','2'],
                ['3','4']
            ])
            csv_path = tmp.name

        try:
            # upload CSV
            self.goto('generate-graph')
            self.driver.find_element(By.ID, "up-file").send_keys(csv_path)
            self.driver.find_element(By.ID, "up-submit_upload").click()
            WebDriverWait(self.driver, 10).until(
                Expect.visibility_of_element_located((By.ID, "ch-graph_type"))
            )

            # configure & preview
            Select(self.driver.find_element(By.ID, "ch-graph_type")).select_by_value("line")
            Select(self.driver.find_element(By.ID, "ch-x_col")).select_by_value("X")
            Select(self.driver.find_element(By.ID, "ch-y_col")).select_by_value("Y")
            self.driver.find_element(By.ID, "ch-submit_generate").click()
            WebDriverWait(self.driver, 10).until(
                Expect.visibility_of_element_located((By.CSS_SELECTOR, "img[src^='data:image/png']"))
            )

            # Save the chart to the database
            self.driver.find_element(By.CSS_SELECTOR, "button.bg-blue-600").click()
            WebDriverWait(self.driver, 10).until(
                Expect.url_to_be(make_path('dashboard'))
            )

            # Grab the newly saved chart from DB
            chart = Chart.query.filter_by(owner_id=self.user.id).first()
            self.assertIsNotNone(chart)

            # 2) Share that chart via chat
            # On the dashboard find the share button for that chart
            share_btn = self.driver.find_element(
                By.CSS_SELECTOR,
                f"button.share-chart-{chart.id}"
            )
            share_btn.click()
            WebDriverWait(self.driver, 10).until(
                Expect.url_to_be(make_path('share-chart', str(chart.id)))
            )

            # Fill out the share form
            Select(self.driver.find_element(By.ID, "recipient")).select_by_value(str(self.friend.id))
            self.driver.find_element(By.ID, "message").send_keys("Check out my new chart!")
            self.driver.find_element(By.ID, "submit_share").click()

            # Verify that a ChatMessage was created
            msg = ChatMessage.query.filter_by(
                sender_id=self.user.id,
                recipient_id=self.friend.id,
                chart_id=chart.id
            ).first()
            self.assertIsNotNone(msg)
            self.assertEqual(msg.content, "Check out my new chart!")
        finally:
            os.remove(csv_path)
