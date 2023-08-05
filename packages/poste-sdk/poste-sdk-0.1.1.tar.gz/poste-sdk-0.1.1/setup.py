# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poste_sdk']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0', 'pydantic>=1.9.1,<2.0.0', 'zmail>=0.2.8,<0.3.0']

setup_kwargs = {
    'name': 'poste-sdk',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'lishulong',
    'author_email': 'lishulong.never@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
