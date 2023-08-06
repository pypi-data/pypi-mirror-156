# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bluetooth_locker']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.6.0,<0.7.0']

entry_points = \
{'console_scripts': ['bluetooth-locker = bluetooth_locker:app']}

setup_kwargs = {
    'name': 'bluetooth-locker',
    'version': '0.1.0',
    'description': 'A bluetooth based locker',
    'long_description': None,
    'author': 'leng-yue',
    'author_email': 'lengyue@lengyue.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
