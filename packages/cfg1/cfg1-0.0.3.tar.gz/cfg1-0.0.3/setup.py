# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cfg1']

package_data = \
{'': ['*']}

install_requires = \
['pyaml>=21.10.1,<22.0.0', 'pytest>=7.1.2,<8.0.0', 'python-box>=6.0.2,<7.0.0']

setup_kwargs = {
    'name': 'cfg1',
    'version': '0.0.3',
    'description': 'A configuration library for Python3 projects',
    'long_description': None,
    'author': 'Dan Sikes',
    'author_email': 'dansikes7@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.0.0,<4.0.0',
}


setup(**setup_kwargs)
