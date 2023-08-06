# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymlpipe']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'pandas>=1.4.3,<2.0.0', 'pytest==5.2', 'sklearn>=0.0,<0.1']

setup_kwargs = {
    'name': 'pymlpipe',
    'version': '0.1.1',
    'description': 'In Development',
    'long_description': None,
    'author': 'Indresh Bhattacharya',
    'author_email': 'indresh2neel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
