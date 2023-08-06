# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kayaku']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'kayaku',
    'version': '0.0.1',
    'description': 'An flexible configuration solution.',
    'long_description': None,
    'author': 'BlueGlassBlock',
    'author_email': 'blueglassblock@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
