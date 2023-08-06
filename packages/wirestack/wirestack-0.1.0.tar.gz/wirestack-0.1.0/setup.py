# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wirestack']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

setup_kwargs = {
    'name': 'wirestack',
    'version': '0.1.0',
    'description': 'WireStack Framework for building fast, scalable websocket apps with aiohttp.',
    'long_description': None,
    'author': 'VincentRPS',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
