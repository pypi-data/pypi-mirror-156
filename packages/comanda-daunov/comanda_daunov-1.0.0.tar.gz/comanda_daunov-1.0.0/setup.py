# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['comanda_daunov']
setup_kwargs = {
    'name': 'comanda-daunov',
    'version': '1.0.0',
    'description': 'rabotay plz',
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
