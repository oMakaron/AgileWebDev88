from unittest import TestCase

from app.services import Parser, ParseError, Tokenizer


class TestParser(TestCase):

    def test_parser(self) -> None:
        tk = Tokenizer('hello = world')
        ps = Parser(tk).parse()
        self.assertEqual({'hello': 'world'}, ps)


    def test_parser_error(self) -> None:
        tk = Tokenizer('hello world')
        with self.assertRaises(ParseError):
            Parser(tk).parse()


    def test_multiple_statements(self) -> None:
        tk = Tokenizer('hello = world, world = earth')
        ps = Parser(tk).parse()
        self.assertEqual({'hello': 'world', 'world': 'earth'}, ps)


    def test_trailing_comma_errors(self) -> None:
        tk = Tokenizer('hello = world, world = earth,')
        with self.assertRaises(ParseError):
            Parser(tk).parse()


    def test_assignment_list(self) -> None:
        tk = Tokenizer('hello = [world, exclamation]')
        ps = Parser(tk).parse()
        self.assertEqual({'hello': ['world', 'exclamation']}, ps)


    def test_assigment_list_one_element(self) -> None:
        tk = Tokenizer('hello = [world]')
        with self.assertRaises(ParseError):
            Parser(tk).parse()


    def test_full_example(self) -> None:
        tk = Tokenizer('type = line, y = [header, header], x = header')
        ps = Parser(tk).parse()
        self.assertEqual({'type': 'line', 'x': 'header', 'y': ['header', 'header']}, ps)


    def test_full_example_with_numbers(self) -> None:
        tk = Tokenizer('type = line, y = [header2, header3], x = header1')
        ps = Parser(tk).parse()
        self.assertEqual({'type': 'line', 'x': 'header1', 'y': ['header2', 'header3']}, ps)


    def test_error_message(self) -> None:
        res = None
        try:
            tk = Tokenizer('type = line, y = [header1,a],')
            Parser(tk).parse()
        except ParseError as p:
            res = str(p)
        self.assertEqual(
            "Parse Error:\n" \
            "type = line, y = [header1,a],\n" \
            "                             ^~ expected a name.",
            res
        )
