# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylink_utils']

package_data = \
{'': ['*']}

install_requires = \
['bs4==0.0.1', 'lxml==4.8.0']

setup_kwargs = {
    'name': 'pylink-utils',
    'version': '1.1.0',
    'description': '',
    'long_description': None,
    'author': 'douglas-peter',
    'author_email': '76939369+douglas-peter@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Pylink-Waterfall/pylink_utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
