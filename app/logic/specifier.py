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
# declaration ::= name '=' (value | '[' value_list ']')
#  value_list ::= value [',' value]+
#       value ::= [a-zA-Z][a-zA-Z0-9]*
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

        # if we didn't match anything it's an error, set has_more to false
        self._has_more = False
        self._head += 1
        return Token.new_error(f'didn\'t recognise this char: {self._get_lexeme()}', self._tail)


class ParseError(Exception):

    def __init__(self, source: str, pos: int, message: str) -> None:
        header = 'Parse Error:'
        outline = f"{' ' * pos}^{'~' * (len(source) - pos)}~ {message}"
        super().__init__('\n'.join((header, source, outline)))




class Parser:

    @staticmethod
    def parse_string(source: str) -> dict[str, str | list[str]]:
        tokens = Tokenizer(source)
        return Parser(tokens).parse()

    def __init__(self, tokens: Tokenizer) -> None:
        self._tokens = tokens
        self._current = Token.new_error('No Tokens!', 0)

    def _match(self, is_a) -> bool:
        return self._current.is_a == is_a

    def _expect(self, is_a: str, message: str) -> str:
        if not self._match(is_a):
            raise ParseError(self._tokens._source, self._current.pos, message)
        return self._current.lex

    def _advance(self) -> None:
        if not self._tokens.has_more():
            self._current = Token.new_error('run out of tokens.', self._tokens._head)
            return
        self._current = self._tokens.next_token()

    def parse(self) -> dict[str, str | list[str]]:
        # entry ::= spec
        self._current = self._tokens.next_token()
        return self._parse_spec()

    def _parse_spec(self) -> dict[str, str | list[str]]:
        # spec ::= decl [',' decl]*
        res = dict()
        while True:
            key, value = self._parse_decl()
            res[key] = value
            if not self._match(','):
                return res
            self._advance()

    def _parse_decl(self) -> Tuple[str, str | list[str]]:
        # decl ::= name '=' (value | '[' value_list ']')
        key = self._parse_name()

        self._expect('=', 'statement requires assignment.')
        self._advance()

        if self._match('['):
            self._advance()
            value = self._parse_value_list()
            self._expect(']', 'brackets were never terminated.')
            self._advance()
        else:
            value = self._parse_value()

        return key, value

    def _parse_value_list(self) -> list[str]:
        # name_list ::= name [',' name]+
        names = []
        read_one = False
        while True:
            names.append(self._parse_value())
            if not self._match(',') and read_one:
                return names
            self._expect(',', 'can\'t have a list of one element.')
            self._advance()
            read_one = True

    def _parse_value(self) -> str:
        # value ::= [a-zA-Z]+[a-zA-Z0-9]*
        if self._match('name'):
            return self._parse_name()
        value = self._expect('value', 'excpected a value')
        self._advance()
        return value

    def _parse_name(self) -> str:
        # name ::= [a-zA-Z]+
        name = self._expect('name', 'expected a name.')
        self._advance()
        return name

