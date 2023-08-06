# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytorch_soo']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pytorch-soo',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Eric Silk',
    'author_email': 'esilk16@uw.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
