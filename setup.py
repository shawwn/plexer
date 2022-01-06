# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['plexer']
setup_kwargs = {
    'name': 'plexer',
    'version': '1.1.0',
    'description': 'A simple lexer to tokenize text (e.g. a C file)',
    'long_description': '',
    'author': 'Shawn Presser',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/shawwn/plexer',
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
