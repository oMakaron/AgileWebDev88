from __future__ import annotations


class Token:
    is_a: str
    lex: str
    pos: int

    def __init__(self, is_a: str, lex: str, pos: int) -> None:
        self.is_a, self.lex, self.pos = is_a, lex, pos

    @staticmethod
    def new_punctuation(value: str, pos: int) -> Token:
        return Token(value, value, pos)

    @staticmethod
    def new_error(message: str, pos: int) -> Token:
        return Token('error', message, pos)

    @staticmethod
    def new_name(value: str, pos: int) -> Token:
        return Token('name', value, pos)

    @staticmethod
    def new_value(value: str, pos: int) -> Token:
        return Token('value', value, pos)


class Tokenizer:

    def __init__(self, source: str) -> None:
        self._source = source
        self._head, self._tail = 0, 0
        self._has_more = True

        self._punctuation = {',', '=', '[', ']'}
        self._alpha = set('abcdefghijklmnopqrstuvwxyz_')
        self._alpha_num = self._alpha | set('0123456789')


    def _at(self, index: int) -> str:
        return self._source[index]

    def _current(self) -> str:
        return self._at(self._head)

    def _test(self, value) -> bool:
        return self._source[self._head : self._head + len(value)] == value

    def _match(self, value: str) -> bool:
        if self._test(value):
            self._head += len(value)
            return True
        return False

    def _get_lexeme(self) -> str:
        return self._source[self._tail : self._head]

    def has_more(self) -> bool:
        return self._has_more and self._head < len(self._source)

    def next_token(self) -> Token:
        # catches tail up to head so that we start reading new token
        self._tail = self._head

        # skips whitespace
        while self._match(' '):
            self._tail = self._head

        if not self._head < len(self._source):
            return Token.new_error('there are no tokens.', self._head)

        # match single character tokens
        for elem in self._punctuation:
            if self._match(elem):
                return Token.new_punctuation(elem, self._tail)

        # matches names
        if self._current().lower() in self._alpha:
            while self.has_more() and self._current().lower() in self._alpha:
                self._head += 1

            # matched values, which can end with a number
            if self.has_more() and self._current().lower() in self._alpha_num:
                while self.has_more() and self._current() in self._alpha_num:
                    self._head += 1
                return Token.new_value(self._get_lexeme(), self._tail)

            return Token.new_name(self._get_lexeme(), self._tail)

        # if we didn't match anything, it's an error, so we set has_more to false
        self._has_more = False
        self._head += 1
        return Token.new_error(f'didn\'t recognise this char: {self._get_lexeme()}', self._tail)