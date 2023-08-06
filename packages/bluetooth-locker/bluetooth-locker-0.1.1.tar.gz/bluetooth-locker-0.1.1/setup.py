# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bluetooth_locker']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['bluetooth-locker = bluetooth_locker.app:main']}

setup_kwargs = {
    'name': 'bluetooth-locker',
    'version': '0.1.1',
    'description': 'A bluetooth based locker',
    'long_description': None,
    'author': 'leng-yue',
    'author_email': 'lengyue@lengyue.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
