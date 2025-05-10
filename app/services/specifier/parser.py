from typing import Tuple

from .tokenizer import Tokenizer, Token


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
