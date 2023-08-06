# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['openapi_python_generator',
 'openapi_python_generator.language_converters',
 'openapi_python_generator.language_converters.python']

package_data = \
{'': ['*'],
 'openapi_python_generator.language_converters.python': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'autopep8>=1.6.0,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'httpx[all]>=0.23.0,<0.24.0',
 'openapi-schema-pydantic>=1.2.3,<2.0.0',
 'orjson>=3.7.2,<4.0.0',
 'pydantic>=1.9.1,<2.0.0']

entry_points = \
{'console_scripts': ['openapi-python-generator = '
                     'openapi_python_generator.__main__:main']}

setup_kwargs = {
    'name': 'openapi-python-generator',
    'version': '0.2.3',
    'description': 'Openapi Python Generator',
    'long_description': "# Openapi Python Generator\n\n[![PyPI](https://img.shields.io/pypi/v/openapi-python-generator.svg)][pypi_]\n[![Status](https://img.shields.io/pypi/status/openapi-python-generator.svg)][status]\n[![Python Version](https://img.shields.io/pypi/pyversions/openapi-python-generator)][python version]\n[![License](https://img.shields.io/pypi/l/openapi-python-generator)][license]\n\n[![Read the documentation at https://openapi-python-generator.readthedocs.io/](https://img.shields.io/readthedocs/openapi-python-generator/latest.svg?label=Read%20the%20Docs)][read the docs]\n[![Tests](https://github.com/MarcoMuellner/openapi-python-generator/workflows/Tests/badge.svg)][tests]\n[![Codecov](https://codecov.io/gh/MarcoMuellner/openapi-python-generator/branch/main/graph/badge.svg)][codecov]\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n\n[pypi_]: https://pypi.org/project/openapi-python-generator/\n[status]: https://pypi.org/project/openapi-python-generator/\n[python version]: https://pypi.org/project/openapi-python-generator\n[read the docs]: https://openapi-python-generator.readthedocs.io/\n[tests]: https://github.com/MarcoMuellner/openapi-python-generator/actions?workflow=Tests\n[codecov]: https://app.codecov.io/gh/MarcoMuellner/openapi-python-generator\n[pre-commit]: https://github.com/pre-commit/pre-commit\n[black]: https://github.com/psf/black\n\n## Features\n\n- Easy code generation for OpenAPI 3.0.0+ APIs\n- Async and Sync code generation support (with the help of [httpx](https://pypi.org/project/httpx/))])\n- Typed services and models for your convinience\n- Support for HttpBearer authentication\n- Python only\n- Usage as CLI tool or as a library\n\n## Requirements\n\n- Python 3.7+\n\n## Installation\n\nYou can install _Openapi Python Generator_ via [pip] from [PyPI]:\n\n```console\n$ pip install openapi-python-generator\n```\n\n## Usage\n\nPlease see the [Command-line Reference] for details.\n\n## Roadmap\n\n- Support for all commonly used http libraries in the python ecosystem (requests, urllib, ...)\n- Support for multiple languages\n- Support for multiple authentication schemes\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [Contributor Guide].\n\n## License\n\nDistributed under the terms of the [MIT license][license],\n_Openapi Python Generator_ is free and open source software.\n\n## Issues\n\nIf you encounter any problems,\nplease [file an issue] along with a detailed description.\n\n## Credits\n\nSpecial thanks to the peeps from [openapi-schema-pydantic](https://github.com/kuimono/openapi-schema-pydantic),\nwhich already did a lot of the legwork by providing a pydantic schema for the OpenAPI 3.0.0+ specification.\n\nThis project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[file an issue]: https://github.com/MarcoMuellner/openapi-python-generator/issues\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[license]: https://github.com/MarcoMuellner/openapi-python-generator/blob/main/LICENSE\n[contributor guide]: https://github.com/MarcoMuellner/openapi-python-generator/blob/main/CONTRIBUTING.md\n[command-line reference]: https://openapi-python-generator.readthedocs.io/en/latest/usage.html\n",
    'author': 'Marco Müllner',
    'author_email': 'muellnermarco@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MarcoMuellner/openapi-python-generator',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
