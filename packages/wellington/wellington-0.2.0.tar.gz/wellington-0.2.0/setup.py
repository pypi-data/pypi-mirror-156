# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wellington', 'wellington.installables', 'wellington.util']

package_data = \
{'': ['*']}

install_requires = \
['tomli>=1.2.2,<2.0.0']

entry_points = \
{'console_scripts': ['well = wellington.cli:run']}

setup_kwargs = {
    'name': 'wellington',
    'version': '0.2.0',
    'description': 'A tool to help bootstrap your dev environment.',
    'long_description': None,
    'author': 'Andrew Halberstadt',
    'author_email': 'ahal@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
