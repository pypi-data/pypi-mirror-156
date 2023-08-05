# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sweetconnect_api']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1']

entry_points = \
{'console_scripts': ['sweetpy = sweetpy.__main__:main']}

setup_kwargs = {
    'name': 'sweetconnect-api',
    'version': '0.0.1',
    'description': 'A SweetConnect API library for Python',
    'long_description': "# SweetConnect API Library\n\n<!-- Uncomment if implemented!\n[![PyPI](https://img.shields.io/pypi/v/sweetpy.svg)][pypi_]\n[![Read the documentation at https://sweetpy.readthedocs.io/](https://img.shields.io/readthedocs/sweetpy/latest.svg?label=Read%20the%20Docs)][read the docs]\n[![Tests](https://gitlab.com/sweetconnect/public/sweetpy/workflows/Tests/badge.svg)][tests]\n[![Codecov](https://codecov.io/gh/cjolowicz/sweetpy/branch/main/graph/badge.svg)][codecov]\n -->\n[![Status](https://img.shields.io/badge/status-Alpha-orange)][status]\n[![License](https://img.shields.io/badge/license-GPL_3.0-green)][license]\n[![Python Version](https://img.shields.io/badge/python-%3E%3D%203.7-blue)][python version]\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n\n<!-- [pypi_]: https://pypi.org/project/sweetpy/\n[read the docs]: https://sweetpy.readthedocs.io/\n[tests]: https://gitlab.com/sweetconnect/public/sweetpy/actions?workflow=Tests\n[codecov]: https://app.codecov.io/gh/cjolowicz/sweetpy\n -->\n\n[status]: https://pypi.org/project/sweetpy/\n[python version]: https://pypi.org/project/sweetpy\n[pre-commit]: https://github.com/pre-commit/pre-commit\n[black]: https://github.com/psf/black\n\n## Features\n\n- TODO\n\n## Requirements\n\n- TODO\n\n## Installation\n\nYou can install _SweetConnect API Library_ via [pip] from [PyPI]:\n\n```console\n$ pip install sweetpy\n```\n\n## Usage\n\nPlease see the [Command-line Reference] for details.\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [Contributor Guide].\n\nThis project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template. For more details see [Hypermodern Python documantation]\n\n## License\n\nDistributed under the terms of the [GPL 3.0 license][license],\n_SweetConnect API Library_ is free and open source software.\n\n## Issues\n\nIf you encounter any problems,\nplease [file an issue] along with a detailed description.\n\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[hypermodern python documantation]: https://cookiecutter-hypermodern-python.readthedocs.io/\n[file an issue]: https://gitlab.com/sweetconnect/public/sweetpy/issues\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[license]: https://gitlab.com/sweetconnect/public/sweetpy/blob/main/LICENSE\n[contributor guide]: https://gitlab.com/sweetconnect/public/sweetpy/blob/main/CONTRIBUTING.md\n[command-line reference]: https://sweetpy.readthedocs.io/en/latest/usage.html\n",
    'author': 'Kai CLauss',
    'author_email': 'kc@sweetconnect.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/sweetconnect/public/sweetpy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
