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

    import plexer
    lines = plexer.tokenize_lines(
        '#include "foo.h"\nint val = 42;\n', plexer.lexers['c'])
    for line in lines:
        if line[0]['value'] == '#include':
            str = ''
            for token in line:
                if token['type'] != plexer.TOKEN_NEWLINE:
                    str = str + token['value']
            print str

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
    version='0.2',
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



