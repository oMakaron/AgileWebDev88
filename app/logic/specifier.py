from __future__ import annotations
from typing import Tuple


# Examples:
#
# style = bar, x = header1, y = header2
# style = line, x = header2, y = [header3, header4]
#

# Grammar:
#
#        spec ::= declaration [',' declaration]*
# declaration ::= name '=' (name | '[' name_list ']')
#   name_list ::= name [',' name]+
#        name ::= [a-zA-Z]+
#


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


class Tokenizer:

    def __init__(self, source: str) -> None:
        self._source = source
        self._head, self._tail = 0, 0
        self._punctuation = {',', '=', '[', ']'}
        self._has_more = True


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

        # match single character tokens
        for elem in self._punctuation:
            if self._match(elem):
                return Token.new_punctuation(elem, self._tail)

        # matches names
        if self._current().lower() in 'abcdefghijklmnopqrstuvwxyz':
            while self.has_more() and self._current().lower() in 'abcdefghijklmnopqrstuvwxyz':
                self._head += 1
            return Token.new_name(self._get_lexeme(), self._tail)

        # if we didn't match anything it's an error, set has_more to false
        self._has_more = False
        self._head += 1
        return Token.new_error(f'didn\'t recognise this char: {self._get_lexeme()}', self._tail)


class ParseError(Exception):
    ...


class Parser:

    def __init__(self, tokens: Tokenizer) -> None:
        self._tokens = tokens
        self._current = Token.new_error('No Tokens!', 0)

    def _expect(self, is_a: str, message: str) -> str:
        if not self._current.is_a == is_a:
            raise ParseError(message)
        return self._current.lex

    def parse(self) -> dict[str, str]:
        self._current = self._tokens.next_token()

        if not self._current.is_a == 'name':
            raise Exception('expected a name')
        key = self._current.lex

        if not self._tokens.has_more():
            raise Exception('statement is incomplete')
        self._current = self._tokens.next_token()

        if not self._current.is_a == '=':
            raise Exception('statement requires an assignment')
        _ = self._current.lex

        if not self._tokens.has_more():
            raise Exception('statement is incomplete')
        self._current = self._tokens.next_token()

        if not self._current.is_a == 'name':
            raise Exception('rhs of assignment requires a value')
        value = self._current.lex

        if self._tokens.has_more():
            raise Exception('expected end of statement')

        return {key: value}


class Specifier:
    dimensions: tuple[int, int]
    x: str | None
    y: str | None

    def __init__(self) -> None:
        self.x, self.y = None, None
        self.dimensions = (10, 8)

    def set_x(self, x: str) -> Specifier:
        self.x = x
        return self

    def set_y(self, y: str) -> Specifier:
        self.y = y
        return self

    @staticmethod
    def from_string(format: str) -> Specifier:

        # TODO: parse in a more robust manner than just split + replace
        spec = dict(elem.split('=') for elem in format.replace(' ', '').split(','))

        if not 'x' in spec or not 'y' in spec:
            raise ValueError("Graph needs both x and y axes to be plotted.")

        return Specifier().set_x(spec['x']).set_y(spec['y'])

