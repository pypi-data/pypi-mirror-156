# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncio_ttl_cache']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'asyncio-ttl-cache',
    'version': '0.0.6',
    'description': 'Async TTL cache',
    'long_description': None,
    'author': 'Pony Ma',
    'author_email': 'mtf201013@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ma-pony/asyncio-ttl-cache',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
