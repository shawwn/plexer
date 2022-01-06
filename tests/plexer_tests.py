"""
    Plexer Tests
    ~~~~~~~~~~~

    Tests the Plexer lexer.

    :copyright: (c) 2010 by Shawn Presser.
    :license: MIT, see LICENSE for more details.
"""
import os
import sys
import unittest
from plexer import LexError, TYPE, TYPE_NAMES, tokenize_lines

example_path = os.path.join(os.path.dirname(__file__), '..', 'examples')
sys.path.append(os.path.join(example_path, 'print_c_includes'))

class BasicFunctionalityTestCase(unittest.TestCase):

    def test_parse_includes(self):
        lines = tokenize_lines(
            '#include <stdio.h>\n#include "myfile.h"\n',
            lexer='c')
        assert len(lines) == 2
        assert lines[0][0]['value'] == '#include'

        # #include <name.h>
        include_global = [
            TYPE.IDENTIFIER, TYPE.WHITESPACE, TYPE.SPECIAL,
            TYPE.IDENTIFIER, TYPE.SPECIAL, TYPE.IDENTIFIER, TYPE.SPECIAL]
        include_global_names = [
            'identifier', 'whitespace', 'special',
            'identifier', 'special', 'identifier', 'special']

        # #include "name.h"
        include_local = [
            TYPE.IDENTIFIER, TYPE.WHITESPACE, TYPE.STRING]
        include_local_names = [
            'identifier', 'whitespace', 'string']

        verify_token_types = [
            include_global, # #include <stdio.h>
            include_local ] # #include "myfile.h"

        verify_token_type_names = [
            include_global_names, # #include <stdio.h>
            include_local_names ] # #include "myfile.h"

        for i in range(len(lines)):
            line = lines[i]
            for j in range(len(line)):
                token = line[j]
                assert token['type'] == verify_token_types[i][j]
                assert token['name'] == verify_token_type_names[i][j]


    def test_fail_parsing_c_block_comment(self):
        try:
            lines = tokenize_lines(
                '#include <stdio.h>\n#int i = 42; /* test \n',
                lexer='c')
        except LexError as e:
            assert e.row == 2
            assert e.col == 14


# def suite():
#     import print_c_includes_tests
#     suite = unittest.TestSuite()
#     suite.addTest(unittest.makeSuite(BasicFunctionalityTestCase))
#     suite.addTest(unittest.makeSuite(print_c_includes_tests.BasicFunctionalityTestCase))
#     return suite


if __name__ == '__main__':
    # unittest.main(defaultTest='suite')
    unittest.main()
