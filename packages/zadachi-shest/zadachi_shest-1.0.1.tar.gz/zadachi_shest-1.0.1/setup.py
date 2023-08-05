# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['zadachi_shest']
setup_kwargs = {
    'name': 'zadachi-shest',
    'version': '1.0.1',
    'description': 'rabotay suka',
    'long_description': None,
    'author': 'NuatStanskiy',
    'author_email': 'smiril13@mail.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
