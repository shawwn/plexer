# constants.
class TYPE:
    NEWLINE     = 0
    WHITESPACE  = 1
    COMMENT     = 2
    NUMBER      = 3
    STRING      = 4
    SPECIAL     = 5 # special language characters such as { } [ ] + - * / etc
    IDENTIFIER  = 6

TYPE_NAMES = {
    TYPE.NEWLINE: 'newline',
    TYPE.WHITESPACE: 'whitespace',
    TYPE.COMMENT: 'comment',
    TYPE.NUMBER: 'number',
    TYPE.STRING: 'string',
    TYPE.SPECIAL: 'special',
    TYPE.IDENTIFIER: 'identifier'
}

# member variables.
LEXERS = { }

#-------------------
# register_lexer(some_lexer, ['ext1', 'ext2'])
#-------------------
def register_lexer(file_extensions, lexer):
    """Associate a lexer with a list of file extensions."""

    if isinstance(file_extensions, str):
        file_extensions = [file_extensions]

    for ext in file_extensions:
        if LEXERS.get(ext):
            print('WARNING: LEXERS[' + ext + '] is being replaced.')
        LEXERS[ext] = lexer

# alias.
add_lexer = register_lexer

def point(ctx: dict, s: str):
    return ctx['pos']

def line(ctx: dict, s: str):
    pt = point(ctx, s)
    return 1 + s[0:pt].count('\n')

def column(ctx: dict, s: str):
    pt = point(ctx, s)
    s2 = s[0:pt]
    i = s2.rfind('\n')
    if i >= 0:
        s2 = s2[i+1:]
    return 1 + len(s2)

#==============================================================================
# LexError
#==============================================================================
class LexError(Exception):

    def __init__(self, msg, ctx: dict, s: str):
        super().__init__(msg)
        self.msg = msg
        self.ctx = dict(ctx)
        self.s = s

    @property
    def row(self):
        return line(self.ctx, self.s)

    @property
    def col(self):
        return column(self.ctx, self.s)



#==============================================================================
# LexNothing:
#==============================================================================
class LexNothing:
    @staticmethod
    def lex(s, idx, end, ctx):
        return 0


#==============================================================================
# LexNewline:
#==============================================================================
class LexNewline:
    """Lex a newline."""

    @staticmethod
    def lex(s, idx, end, ctx):

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
    def lex(s, idx, end, ctx):
        if s[idx] == ' ' or \
           s[idx] == '\t':
            return 1
        return 0

#==============================================================================
# Lexer
#==============================================================================
class Lexer:
    """Determines how to divide the input stream into tokens."""

    def __init__(self, 
                 lex_comment=LexNothing,
                 lex_number=LexNothing,
                 lex_string=LexNothing,
                 special_chars='',
                 identifier_chars=''):
        self.lex_comment = lex_comment
        self.lex_number = lex_number
        self.lex_string = lex_string
        self.special_chars = special_chars
        self.identifier_chars = identifier_chars

#******************************************************************************
# Basic Lexer
#******************************************************************************

#==============================================================================
# LexBasicNumber
#==============================================================================

class LexBasicNumber:
    """Lex an integer, decimal, or decimal + exponent.  Examples:

        2
        .9
        .9e2
        -42
    """

    @staticmethod
    def lex(s, idx, end, ctx):
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
                    # otherwise, there is an actual exponent, so we are no
                    # longer an integer.
                    is_integer = False

        return idx - start

# associate the basic lexer with various filetypes.
add_lexer(
    ['', 'txt'],
    Lexer(lex_number=LexBasicNumber))

#******************************************************************************
# C lexer
#******************************************************************************

#==============================================================================
# LexCComment
#==============================================================================
class LexCComment:
    """Lex a C comment."""

    @staticmethod
    def lex(s, idx, end, ctx):

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
                if s[idx] == '\n':
                    ctx['line'] = ctx['line'] + 1
                if s[idx] == '*':
                    if idx + 1 < end and s[idx+1] == '/':
                        return (idx + 2) - start
                idx = idx + 1
            # if we couldn't find the termination of the block comment, then
            # raise an exception.
            raise LexError("Unterminated C block comment", ctx, s)

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
    def lex(s, idx, end, ctx):
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
                    # otherwise, there is an actual exponent, so we are no
                    # longer an integer.
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
    def lex(s, idx, end, ctx):
        if s[idx] != '"':
            return 0

        # catch the following: '\"'
        if idx > 0:
            if s[idx-1] == '\\':
                return 0

        # catch the following: '"'
        if idx > 0 and idx < end-1:
            if s[idx-1] == "'" and s[idx+1] == "'":
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
        raise LexError("String not terminated", ctx, s)

# associate the c lexer with various filetypes.
add_lexer(['c', 'h', 'cpp', 'hpp'],
          Lexer(
              lex_comment=LexCComment,
              lex_number=LexCNumber,
              lex_string=LexCString,
              special_chars=".,:;!=-+/*&<>()[]{}",
              identifier_chars="_"))

#******************************************************************************
# lex
#******************************************************************************

def tokenize(s,
             lexer='cpp'):
    idx = 0
    end = len(s)
    lines = []
    tokens = []
    ctx = {'line': 1, 'column': 1, 'pos': 0, 'offset': 0}

    # lookup lexer.
    ext = lexer.lower()
    if not ext in LEXERS:
        raise LexError("No lexer associated with '" + ext + "', use add_lexer", ctx, s)
    lexer = LEXERS[ext]

    # idenfier index / end
    id_idx = 0
    id_end = -1
    def append_token(type, idx, val):
        return tokens.append({
            'type': type,
            'name': TYPE_NAMES[type],
            'value': val,
            'line': ctx['line'],
            'column': ctx['column']})

    def add_token(type, s, idx, end):
        if id_end > 0:
            append_token(TYPE.IDENTIFIER, id_idx, s[id_idx:id_end])
        append_token(type, idx, s[idx:end])

    while idx < end:
        start = idx
        ctx['pos'] = idx
        ctx['column'] = id_idx - ctx['offset'] + 1

        # comment?
        idx = idx + lexer.lex_comment.lex(s, idx, end, ctx)
        if idx != start:
            add_token(TYPE.COMMENT, s, start, idx)
            id_idx = idx
            id_end = -1
            continue

        # newline?
        idx = idx + LexNewline.lex(s, idx, end, ctx)
        if idx != start:
            add_token(TYPE.NEWLINE, s, start, idx)
            ctx['line'] = ctx['line'] + 1
            ctx['offset'] = idx
            id_idx = idx
            id_end = -1
            continue

        # whitespace?
        idx = idx + LexWhitespace.lex(s, idx, end, ctx)
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
        if id_end <= 0:
            idx = idx + lexer.lex_number.lex(s, idx, end, ctx)
            if idx != start:
                add_token(TYPE.NUMBER, s, start, idx)
                id_idx = idx
                id_end = -1
                continue

        # string?
        idx = idx + lexer.lex_string.lex(s, idx, end, ctx)
        if idx != start:
            add_token(TYPE.STRING, s, start, idx)
            id_idx = idx
            id_end = -1
            continue

        # identifier.
        idx = idx + 1
        id_end = idx

    if id_end > 0:
        append_token(TYPE.IDENTIFIER, id_idx, s[id_idx:id_end])

    return tokens


def tokenize_lines(s,
                   strip_newlines=True,
                   lexer='cpp'):
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

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    with open(filename) as f:
        lines = tokenize_lines(f.read())
    from pprint import pprint as pp
    filtered = [x[i] for x in lines for i in range(len(x)) if x[i]['type'] != 'whitespace']
    pp(filtered)
