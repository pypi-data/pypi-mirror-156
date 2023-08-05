# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycmodels']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pycmodels',
    'version': '0.1.0',
    'description': 'A python library for simulating multiples models of computation.',
    'long_description': None,
    'author': 'Luis Papiernik',
    'author_email': 'lpapiernik24@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
