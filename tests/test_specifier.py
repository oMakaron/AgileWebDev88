from unittest import TestCase

from app.logic.specifier import ParseError, Parser, Tokenizer


class Test(TestCase):

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

    def test_tokenizer_fails_on_empty(self) -> None:
        tk = Tokenizer('').next_token()
        self.assertEqual('error', tk.is_a)
        self.assertEqual('there are no tokens.', tk.lex)

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

    def test_tokenizer_tokenizes_value(self) -> None:
        tk = Tokenizer('hello = [world, exclamationmark42]')

        res = []
        while tk.has_more():
            res.append(tk.next_token())

        self.assertEqual(
            ['hello', '=', '[', 'world', ',', 'exclamationmark42', ']'],
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

