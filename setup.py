"""
Plexer
-----

Plexer is a simple lexer (tokenizer) for Python.

License: MIT

How to...?
````````````

-----
Print all #include statements in a C/C++ file?
-----

    from plexer import TYPE, tokenize_lines

    lines = tokenize_lines('#include "foo.h"\nint val = 42;\n')
    for line in lines:
        first_token = line[0]
        if first_token['value'] == '#include':
            # print the line.
            print ''.join([token['value'] for token in line])

-----
Setup?
-----

    $ easy_install Plexer

Links
`````

* `website <http://github.com/shawnpresser/plexer/>`_

"""
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup

def run_tests():
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
    from plexer_tests import suite
    return suite()

setup(
    name='Plexer',
    version='0.3.1',
    url='http://github.com/shawnpresser/plexer/',
    license='MIT',
    author='Shawn Presser',
    author_email='shawnpresser@gmail.com',
    description='A simple lexer to tokenize text (for example, a C file)',
    keywords='lexer tokenize tokenization parser text',
    py_modules=['distribute_setup','plexer'],
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='__main__.run_tests'
)



