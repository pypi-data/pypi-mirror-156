# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dummy_pkg']

package_data = \
{'': ['*']}

install_requires = \
['scipy>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'dummy-pkg',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'glaunay',
    'author_email': 'pitooon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
