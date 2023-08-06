# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vincaweb']

package_data = \
{'': ['*'], 'vincaweb': ['templates/*']}

install_requires = \
['Flask>=2.1.2,<3.0.0', 'vinca>=2.4.7,<3.0.0']

setup_kwargs = {
    'name': 'vincaweb',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Oscar Laird',
    'author_email': 'olaird25@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
