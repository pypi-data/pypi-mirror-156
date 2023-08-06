# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cfg1']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cfg1',
    'version': '0.0.0',
    'description': 'A configuration library for Python3 projects',
    'long_description': None,
    'author': 'Dan Sikes',
    'author_email': 'dansikes7@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
