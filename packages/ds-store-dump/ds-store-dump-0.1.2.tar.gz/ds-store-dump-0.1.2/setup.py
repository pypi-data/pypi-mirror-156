# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ds_store_dump', 'ds_store_dump.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3.0.0,<4.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'cchardet>=2.1.7,<3.0.0',
 'click>=8.1.3,<9.0.0',
 'ds-store>=1.3.0,<2.0.0']

entry_points = \
{'console_scripts': ['ds-store-dump = ds-store-dump:cli']}

setup_kwargs = {
    'name': 'ds-store-dump',
    'version': '0.1.2',
    'description': 'Dump backups and another files using .DS_Store',
    'long_description': None,
    'author': 'tz4678',
    'author_email': 'tz4678@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
