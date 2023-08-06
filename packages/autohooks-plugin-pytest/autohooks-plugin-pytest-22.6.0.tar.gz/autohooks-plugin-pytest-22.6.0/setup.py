# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autohooks', 'autohooks.plugins.pytest']

package_data = \
{'': ['*']}

install_requires = \
['autohooks>=21.3.0,<22.0.0', 'flake8>=4.0.1,<5.0.0', 'pytest>=7.1.2,<8.0.0']

setup_kwargs = {
    'name': 'autohooks-plugin-pytest',
    'version': '22.6.0',
    'description': 'An autohooks plugin for pytest',
    'long_description': '![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)\n\n# autohooks-plugin-pytest\n\n[![PyPI release](https://img.shields.io/pypi/v/autohooks-plugin-pytest.svg)](https://pypi.org/project/autohooks-plugin-pytest/)\n\nAn [autohooks](https://github.com/greenbone/autohooks) plugin for [pytest](https://github.com/pytest-dev/pytest/).\n\n## Installation\n\n### Install using pip\n\nYou can install the latest stable release of autohooks-plugin-pytest from the\nPython Package Index using [pip](https://pip.pypa.io/):\n\n    python3 -m pip install autohooks-plugin-pytest\n\n### Install using poetry\n\nIt is highly encouraged to use [poetry](https://python-poetry.org) for\nmaintaining your project\'s dependencies. Normally autohooks-plugin-pytest is\ninstalled as a development dependency.\n\n    poetry install\n\n## Usage\n\nTo activate the pytest autohooks plugin please add the following setting to your\n*pyproject.toml* file.\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.pytest"]\n```\n\nBy default, autohooks plugin pytest checks all files with a *.py* ending. If\nonly files in a sub-directory or files with different endings should be\ntested, just add the following setting:\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.pytest"]\n\n[tool.autohooks.plugins.pytest]\ninclude = [\'foo/*.py\', \'*.foo\']\n```\n\nBy default, autohooks plugin pytest executes pytest without any arguments and\npytest settings are loaded from the *.pytestrc* file in the root directory of\ngit repository. To change specific settings or to define a different pytest rc\nfile the following plugin configuration can be used:\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.pytest"]\n\n[tool.autohooks.plugins.pytest]\narguments = ["--rcfile=/path/to/pytestrc", "-s", "n"]\n```\n\n## Maintainer\n\nThis project is maintained by [Greenbone Networks GmbH](https://www.greenbone.net/).\n\n## Contributing\n\nYour contributions are highly appreciated. Please\n[create a pull request](https://github.com/greenbone/autohooks-plugin-pytest/pulls)\non GitHub. Bigger changes need to be discussed with the development team via the\n[issues section at GitHub](https://github.com/greenbone/autohooks-plugin-pytest/issues)\nfirst.\n\n## License\n\nCopyright (C) 2021-2022 [Greenbone Networks GmbH](https://www.greenbone.net/)\n\nLicensed under the [GNU General Public License v3.0 or later](LICENSE).\n',
    'author': 'Greenbone Networks GmbH',
    'author_email': 'info@greenbone.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/greenbone/autohooks-plugin-pytest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
