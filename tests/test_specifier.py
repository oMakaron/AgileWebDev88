from unittest import TestCase

from app.logic.specifier import ParseError, Parser, Specifier, Tokenizer


class Test(TestCase):

    # Specifier Tests

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

    # Tokenizer tests

    def test_test_true(self) -> None:
        tk = Tokenizer('hello, world!')
        self.assertTrue(tk._test('hello,'))

    def test_test_false(self) -> None:
        tk = Tokenizer('hello, world!')
        self.assertFalse(tk._test('bello,'))

    def test_test_in_middle(self) -> None:
        tk = Tokenizer('hello, world!')
        tk._head += 3
        self.assertTrue(tk._test('lo, wo'))

    def test_match_true(self) -> None:
        tk = Tokenizer('hello, world!')
        self.assertTrue(tk._match('hello,'))
        self.assertEqual(6, tk._head)

    def test_match_false(self) -> None:
        tk = Tokenizer('hello, world!')
        self.assertFalse(tk._match('bello,'))
        self.assertEqual(0, tk._head)

    def test_tokenizer_stops_with_error(self) -> None:
        tk = Tokenizer('hello = [world, exclamationmark]>')

        res = []
        while tk.has_more():
            res.append(tk.next_token())

        self.assertEqual(
            ['hello', '=', '[', 'world', ',', 'exclamationmark', ']', 'didn\'t recognise this char: >'],
            [elem.lex for elem in res]

        )

    def test_tokenizer_stops_itself_simple(self) -> None:
        tk = Tokenizer('hello = world')

        res = []
        while tk.has_more():
            res.append(tk.next_token())

        self.assertEqual(
            ['hello', '=', 'world'],
            [elem.lex for elem in res]

        )

    def test_tokenizer_stops_itself(self) -> None:
        tk = Tokenizer('hello = [world, exclamationmark]')

        res = []
        while tk.has_more():
            res.append(tk.next_token())

        self.assertEqual(
            ['hello', '=', '[', 'world', ',', 'exclamationmark', ']'],
            [elem.lex for elem in res]
        )

    # Parser tests

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

