# -*- coding: utf-8 -*-
"""
    Print C Includes
    ~~~~~~

    Lexes a C file and prints any #include statements.

    :copyright: (c) 2010 by Shawn Presser.
    :license: MIT, see LICENSE for more details.
"""
import plexer
from plexer import TYPE, tokenize_lines

def print_includes(s):
    lines = tokenize_lines(s, 'c')
    for line in lines:
        if line:
            if line[0]['value'] == '#include':
                p = ''
                for token in line:
                    p = p + token['value']
                print(p)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: print_c_includes.py <C/C++ file name>")
    else:
        try:
            print_includes(open(sys.argv[1], 'r').read())
        except IOError:
            print("Could not open file '" + sys.argv[1] + "' for reading.")

