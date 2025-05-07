from .parser import Parser, ParseError

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
