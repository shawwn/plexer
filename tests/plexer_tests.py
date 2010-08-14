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
import plexer

example_path = os.path.join(os.path.dirname(__file__), '..', 'examples')
sys.path.append(os.path.join(example_path, 'print_c_includes'))

class BasicFunctionalityTestCase(unittest.TestCase):

    def test_parse_includes(self):
        lines = plexer.tokenize_lines(
            '#include <stdio.h>\n#include <stdlib.h>\n',
            plexer.lexers['c'])
        assert len(lines) == 2
        assert lines[0][0]['value'] == '#include'

def suite():
    import print_c_includes_tests 
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BasicFunctionalityTestCase))
    suite.addTest(unittest.makeSuite(print_c_includes_tests.BasicFunctionalityTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
