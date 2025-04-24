from unittest import TestCase

from app.logic.specifier import Specifier


class Test(TestCase):

    def test_given_headers(self) -> None:
        result = Specifier.from_string('x=x,y=y')
        self.assertEqual(('x', 'y'), (result.x, result.y))

    def test_can_have_spaces(self) -> None:
        result = Specifier.from_string('x = x, y = header')
        self.assertEqual(('x', 'header'), (result.x, result.y))

    def test_given_one_header(self) -> None:
        with self.assertRaises(ValueError):
            Specifier.from_string('x=x')

    def test_given_no_headers(self) -> None:
        with self.assertRaises(ValueError):
            Specifier.from_string('')

