# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sequal']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sequal',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': 'Toan Phung',
    'author_email': 'toan.phungkhoiquoctoan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
