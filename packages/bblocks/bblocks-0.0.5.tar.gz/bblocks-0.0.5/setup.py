# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bblocks',
 'bblocks.analysis_tools',
 'bblocks.cleaning_tools',
 'bblocks.dataframe_tools',
 'bblocks.import_tools',
 'bblocks.other_tools',
 'tests',
 'tests.test_analysis_tools',
 'tests.test_cleaning_tools',
 'tests.test_dataframe_tools',
 'tests.test_import_tools',
 'tests.test_other_tools']

package_data = \
{'': ['*'], 'bblocks.import_tools': ['stored_data/*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'country-converter>=0.7.4,<0.8.0',
 'numpy>=1.23.0,<2.0.0',
 'openpyxl>=3.0.10,<4.0.0',
 'pyarrow>=8.0.0,<9.0.0',
 'requests>=2.28.0,<3.0.0',
 'wbgapi>=1.1.2,<2.0.0',
 'xlrd>=2.0.1,<3.0.0']

extras_require = \
{':extra == "test" or extra == "dev" or extra == "doc"': ['pandas>=1.4.3,<2.0.0'],
 'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocstrings>=0.15.2,<0.16.0',
         'mkdocs-autorefs>=0.2.1,<0.3.0'],
 'test': ['black>=21.5b2,<22.0',
          'isort>=5.8.0,<6.0.0',
          'flake8>=3.9.2,<4.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'mypy>=0.900,<0.901',
          'pytest>=6.2.4,<7.0.0',
          'pytest-cov>=2.12.0,<3.0.0']}

entry_points = \
{'console_scripts': ['bblocks = bblocks.cli:main']}

setup_kwargs = {
    'name': 'bblocks',
    'version': '0.0.5',
    'description': 'A package with tools to download and analyse international development data.',
    'long_description': '# bblocks\n\n\n[![pypi](https://img.shields.io/pypi/v/bblocks.svg)](https://pypi.org/project/bblocks/)\n[![python](https://img.shields.io/pypi/pyversions/bblocks.svg)](https://pypi.org/project/bblocks/)\n[![Build Status](https://github.com/ONECampaign/bblocks/actions/workflows/dev.yml/badge.svg)](https://github.com/ONECampaign/bblocks/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/ONECampaign/bblocks/branch/main/graphs/badge.svg)](https://codecov.io/github/ONECampaign/bblocks)\n\n\n\nA package with tools to download and analyse international development data\n\n\n* Documentation: <https://ONECampaign.github.io/bblocks>\n* GitHub: <https://github.com/ONECampaign/bblocks>\n* PyPI: <https://pypi.org/project/bblocks/>\n* Free software: MIT\n\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n',
    'author': 'The ONE Campaign',
    'author_email': 'data@one.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ONECampaign/bblocks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
