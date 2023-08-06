# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qdbg']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'qdbg',
    'version': '0.0.3',
    'description': 'quick debugging cli tool',
    'long_description': None,
    'author': 'Jimmy Herman',
    'author_email': 'jimmyherman29@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hermgerm29/qdbg',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
