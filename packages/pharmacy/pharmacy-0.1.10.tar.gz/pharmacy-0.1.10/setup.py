# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pharmacy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pharmacy',
    'version': '0.1.10',
    'description': 'The pharmacy module is a set of utilities for use with hospital and retail pharmacy data.',
    'long_description': None,
    'author': 'Danny Limoges, PharmD',
    'author_email': 'pharmacydataland@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
