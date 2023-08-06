# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['startfile']
setup_kwargs = {
    'name': 'startfile',
    'version': '1.0.0',
    'description': 'hi this help from star python',
    'long_description': None,
    'author': 'None',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
