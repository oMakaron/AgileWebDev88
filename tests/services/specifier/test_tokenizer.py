from unittest import TestCase

from app.services import Tokenizer


class TestTokenizer(TestCase):

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
