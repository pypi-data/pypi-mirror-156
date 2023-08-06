# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dojima', 'dojima.brokers']

package_data = \
{'': ['*']}

install_requires = \
['black>=22.3.0,<23.0.0']

setup_kwargs = {
    'name': 'dojima',
    'version': '0.1.0',
    'description': 'an interface for crypto derivative apis\x1bb',
    'long_description': None,
    'author': 'Rahul',
    'author_email': 'haxdds@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
