# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autohooks', 'autohooks.plugins.flake8', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['autohooks>=21.3.0,<22.0.0', 'flake8==4.0.1', 'pylint==2.13.9']

setup_kwargs = {
    'name': 'autohooks-plugin-flake8',
    'version': '22.6.1',
    'description': 'An autohooks plugin for python code linting via flake8.',
    'long_description': '![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)\n\n# autohooks-plugin-flake8\n\n[![PyPI release](https://img.shields.io/pypi/v/autohooks-plugin-flake8.svg)](https://pypi.org/project/autohooks-plugin-flake8/)\n\nAn [autohooks](https://github.com/greenbone/autohooks) plugin for python code\nlinting via [flake8](https://github.com/PyCQA/flake8).\n\n## Installation\n\n### Install using pip\n\nYou can install the latest stable release of autohooks-plugin-flake8 from the\nPython Package Index using [pip](https://pip.pypa.io/):\n\n    python3 -m pip install autohooks-plugin-flake8\n\nNote the `pip` refers to the Python 3 package manager. In an environment where\nPython 2 is also available the correct command may be `pip3`.\n\n### Install using poetry\n\nIt is highly encouraged to use [poetry](https://python-poetry.org) for\nmaintaining your project\'s dependencies. Normally autohooks-plugin-flake8 is\ninstalled as a development dependency.\n\n    poetry install\n\n## Usage\n\nTo activate the flake8 autohooks plugin please add the following setting to your\n*pyproject.toml* file.\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.flake8"]\n```\n\nBy default, autohooks plugin flake8 checks all files with a *.py* ending. If\nonly files in a sub-directory or files with different endings should be\nformatted, just add the following setting:\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.flake8"]\n\n[tool.autohooks.plugins.flake8]\ninclude = [\'foo/*.py\', \'*.foo\']\n```\n\nTo configure flake8 you can specify command-line options in the default flake8 \nconfiguration file *.flake8* in the root directory of the git repository.\nTo learn more about flake8 configuration see the configuration file or\nthe flake8 documentation. You can specify your own configuration file using \n\n```\narguments = ["--config=/path/to/flake8config"]\n```\n\ninside the `[tool.autohooks.plugins.flake8]` section of your projects `pyproject.toml`.\n\nSee `flake8 --help` for more details.\n\n## Maintainer\n\nThis project is maintained by [Greenbone Networks GmbH](https://www.greenbone.net/).\n\n## Contributing\n\nYour contributions are highly appreciated. Please\n[create a pull request](https://github.com/greenbone/autohooks-plugin-flake8/pulls)\non GitHub. Bigger changes need to be discussed with the development team via the\n[issues section at GitHub](https://github.com/greenbone/autohooks-plugin-flake8/issues)\nfirst.\n\n## License\n\nCopyright (C) 2019 - 2022 [Greenbone Networks GmbH](https://www.greenbone.net/)\n\nLicensed under the [GNU General Public License v3.0 or later](LICENSE).\n\nSPDX-License-Identifier: GPL-3.0-or-later\n',
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
