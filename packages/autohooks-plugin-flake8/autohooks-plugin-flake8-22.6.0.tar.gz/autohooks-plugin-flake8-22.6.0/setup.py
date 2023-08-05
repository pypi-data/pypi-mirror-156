# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autohooks', 'autohooks.plugins.flake8']

package_data = \
{'': ['*']}

install_requires = \
['autohooks>=21.3.0,<22.0.0', 'flake8==4.0.1', 'pylint==2.13.9']

setup_kwargs = {
    'name': 'autohooks-plugin-flake8',
    'version': '22.6.0',
    'description': 'An autohooks plugin for python code linting via flake8.',
    'long_description': None,
    'author': 'Greenbone Networks GmbH',
    'author_email': 'info@greenbone.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
