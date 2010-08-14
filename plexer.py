#==============================================================================
# Constants
#==============================================================================

class TYPE:
    NEWLINE     = 0
    WHITESPACE  = 1
    COMMENT     = 2
    NUMBER      = 3
    STRING      = 4
    SPECIAL     = 5 # special language characters such as { } [ ] + - * / etc
    IDENTIFIER  = 6

type_names = [
    'newline',
    'whitespace',
    'comment',
    'number',
    'string',
    'special',
    'identifier']

#==============================================================================
# Error
#==============================================================================
class Error(Exception):
    """Base class for exceptions in this module."""
    pass


#==============================================================================
# LexerError
#==============================================================================
class LexerError(Error):
    """Exception raised for errors in the input stream.

    Attributes:
        ctx -- the current context of the lexer
        msg -- explanation of the Error
    """

    def __init__(self, ctx, msg):
        self.ctx = ctx
        self.msg = msg

#==============================================================================
# LexNewline:
#==============================================================================
class LexNewline:
    """Lex a newline."""

    @staticmethod
    def lex(s, idx, end):

        # UNIX-style newline.
        if s[idx] == '\n':
            return 1

        # Windows-style newline.
        if s[idx] == '\r':
            if idx + 1 < end:
                if s[idx+1] == '\n':
                    return 2

        return 0

#==============================================================================
# LexWhitespace:
#==============================================================================
class LexWhitespace:
    """Lex whitespace."""

    @staticmethod
    def lex(s, idx, end):
        if s[idx] == ' ' or \
           s[idx] == '\t':
            return 1
        return 0

#==============================================================================
# Lexer
#==============================================================================
class Lexer:
    """Defines how the input stream is divided into tokens.

    """

    def __init__(self, 
                 lex_comment,
                 lex_number,
                 lex_string,
                 special_chars,
                 identifier_chars):
        self.lex_comment = lex_comment
        self.lex_number = lex_number
        self.lex_string = lex_string
        self.special_chars = special_chars
        self.identifier_chars = identifier_chars


#******************************************************************************
# C lexer rules
#******************************************************************************

#==============================================================================
# LexCComment
#==============================================================================
class LexCComment:
    """Lex a C comment."""

    @staticmethod
    def lex(s, idx, end):

        if s[idx] != '/':
            return 0

        if idx + 1 >= end:
            return 0

        start = idx
        idx = idx + 1

        # C line comment
        if s[idx] == '/':
            idx = idx + 1
            while idx < end:
                # we're done if we've hit a UNIX-style newline.
                if s[idx] == '\n':
                    break
                # we're done if we've hit a Window-style newline.
                if s[idx] == '\r':
                    if idx + 1 < end and s[idx+1] == '\n':
                        break
                idx = idx + 1
            return idx - start

        # C block comment
        if s[idx] == '*':
            idx = idx + 1
            while idx < end:
                if s[idx] == '*':
                    if idx + 1 < end and s[idx+1] == '/':
                        return (idx + 2) - start
                idx = idx + 1
            # if we couldn't find the termination of the block comment, then
            # raise an exception.
            raise Error("Unterminated C block comment")

        return 0

#==============================================================================
# LexCNumber
#==============================================================================

class LexCNumber:
    """Lex a C integer, float, or double literal.  Examples:

        2
        .9f or .9F
        .9e2 or .9E2
        2.5e-3f
        -51UL (yes, this is valid C)
    """

    @staticmethod
    def lex(s, idx, end):
        start = idx
        num_digits = 0
        num_decimals = 0
        decimal_idx = None
        is_integer = True

        # skip over the negation.
        if s[idx] == '-':
            idx = idx + 1

        # skip over the integer component.
        num_start = idx
        while idx < end and s[idx] >= '0' and s[idx] <= '9':
            idx = idx + 1
        num_digits = idx - num_start

        # skip over the decimal component.
        if idx < end and s[idx] == '.':
            # skip the decimal character.
            is_integer = False
            decimal_idx = idx
            idx = idx + 1

            # skip the decimal numbers.
            num_start = idx
            while idx < end and s[idx] >= '0' and s[idx] <= '9':
                idx = idx + 1
            num_decimals = idx - num_start
            num_digits = num_digits + num_decimals

        # if we have no digits, then abort.
        if num_digits == 0:
            return 0

        # do we have an exponent?
        if idx < end and (s[idx] == 'e' or s[idx] == 'E'):

            # we must either have no decimal character or at least one
            # decimal digit to have an exponent.
            if decimal_idx == None or num_decimals > 0:

                # save the starting index of the exponent.
                exp_start = idx

                # skip over the exponent character.
                idx = idx + 1

                # skip over the exponent negation.
                if idx < end and s[idx] == '-':
                    idx = idx + 1

                # skip over the exponent integer.
                num_start = idx
                while idx < end and s[idx] >= '0' and s[idx] <= '9':
                    idx = idx + 1

                # if there is no exponent integer, then there is no exponent,
                # so rewind.
                if idx - num_start <= 0:
                    idx = exp_start
                else:
                    # otherwise, there is an actual exponent, so we are no longer
                    # an integer.
                    is_integer = False

        if is_integer:
            # skip the unsigned postfix.
            if idx < end and (s[idx] == 'u' or s[idx] == 'U'):
                idx = idx + 1

            # skip the long postfix.
            if idx < end and (s[idx] == 'l' or s[idx] == 'L'):
                idx = idx + 1
        else:
            # skip the float postfix.
            if idx < end and (s[idx] == 'f' or s[idx] == 'F'):
                idx = idx + 1

        return idx - start

#==============================================================================
# LexCString:
#==============================================================================
class LexCString:
    """Lex a C string."""

    @staticmethod
    def lex(s, idx, end):
        if s[idx] != '"':
            return 0

        # find the closing quote.
        start = idx
        idx = idx + 1
        while idx < end:
            # if we've found the closing quote, we're done.
            if s[idx] == '"' and s[idx-1] != "\\":
                return (idx + 1) - start
            idx = idx + 1

        # if no closing quote could be found, raise an exception.
        raise Error("String not terminated")

#******************************************************************************
# lex
#******************************************************************************

lexers = {
    'c': Lexer(
        LexCComment,
        LexCNumber,
        LexCString,
        ".,:;!=-+/*&<>()[]{}",
        "_")
}

def tokenize(s, lexer = lexers['c']):
    idx = 0
    end = len(s)
    lines = []
    tokens = []

    # idenfier index / end
    id_idx = 0
    id_end = -1
    def append_token(type, val):
        return tokens.append({
            'type' : type,
            'name': type_names[type],
            'value': val})

    def add_token(type, s, idx, end):
        if id_end > 0:
            append_token(TYPE.IDENTIFIER, s[id_idx:id_end])
        append_token(type, s[idx:end])

    while idx < end:
        start = idx

        # comment?
        idx = idx + lexer.lex_comment.lex(s, idx, end)
        if idx != start:
            add_token(TYPE.COMMENT, s, start, idx)
            id_idx = idx
            id_end = -1
            continue

        # newline?
        idx = idx + LexNewline.lex(s, idx, end)
        if idx != start:
            add_token(TYPE.NEWLINE, s, start, idx)
            id_idx = idx
            id_end = -1
            continue

        # whitespace?
        idx = idx + LexWhitespace.lex(s, idx, end)
        if idx != start:
            add_token(TYPE.WHITESPACE, s, start, idx)
            id_idx = idx
            id_end = -1
            continue

        # special?
        if lexer.special_chars.find(s[idx]) >= 0:
            idx = idx + 1
            add_token(TYPE.SPECIAL, s, start, idx)
            id_idx = idx
            id_end = -1
            continue

        # number?
        idx = idx + lexer.lex_number.lex(s, idx, end)
        if idx != start:
            add_token(TYPE.NUMBER, s, start, idx)
            id_idx = idx
            id_end = -1
            continue

        # string?
        idx = idx + lexer.lex_string.lex(s, idx, end)
        if idx != start:
            add_token(TYPE.STRING, s, start, idx)
            id_idx = idx
            id_end = -1
            continue

        # identifier.
        idx = idx + 1
        id_end = idx

    if id_end > 0:
        append_token(TYPE.IDENTIFIER, s[id_idx:id_end])

    return tokens


def tokenize_lines(s,
              lexer = lexers['c'],
              strip_newlines = True):
    tokens = tokenize(s, lexer)
    lines = []
    line_tokens = []
    for token in tokens:
        if token['type'] == TYPE.NEWLINE:
            if not strip_newlines:
                line_tokens.append(token)
            lines.append(line_tokens)
            line_tokens = []
        else:
            line_tokens.append(token)

    if len(line_tokens) > 0:
        lines.append(line_tokens)
        line_tokens = []

    return lines

