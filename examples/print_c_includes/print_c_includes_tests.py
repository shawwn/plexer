"""
    Print C Includes Tests
    ~~~~~~~~~~~

    Tests the Print C Includes example.

    :copyright: (c) 2010 by Shawn Presser.
    :license: MIT, see LICENSE for more details.
"""
import unittest
import print_c_includes

class BasicFunctionalityTestCase(unittest.TestCase):
    def test_print_includes(self):
        print_c_includes.print_includes(
            '#include <stdio.h>\n#include <stdlib.h>\nint i = 42;\n')

if __name__ == '__main__':
    unittest.main()
