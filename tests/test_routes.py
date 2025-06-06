from unittest import TestCase
from io import BytesIO

from app import create_app
from config import TestConfig

Data = str | int | float

def make_csv(name: str, data: list[list[Data]]) -> tuple[BytesIO, str]:
    rows = [','.join([str(element) for element in row]) for row in data]
    contents = '\n'.join(rows).encode('utf-8')
    return BytesIO(contents), name


class Test(TestCase):

    def setUp(self) -> None:
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def test_index(self) -> None:
        result = self.client.get('/')
        self.assertEqual(200, result.status_code)

    def test_login(self) -> None:
        result = self.client.get('/login')
        self.assertEqual(200, result.status_code)

    def test_upload(self) -> None:
        data = {
            'file': make_csv( 'test.csv', [ ['Header1', 'Header2', 'Header3'],
                                            ['Body1',   'Body2',   '3'],
                                            ['Body4',   'Body5',   '6'], ]),
            'spec': "type = bar, x_col = Header1, y_col = Header3"
        }

        response = self.client.post('/upload', data=data, content_type='multipart/form-data')

        self.assertEqual(200, response.status_code)
        self.assertIn(b"<img src=", response.data)
