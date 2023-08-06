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
['click>=8.1.3,<9.0.0', 'wbgapi>=1.1,<2.0', 'wheel>=0.37.1,<0.38.0']

extras_require = \
{':extra == "dev"': ['twine>=4.0.1,<5.0.0'],
 ':extra == "dev" or extra == "doc"': ['numpy>=1.23,<2.0',
                                       'country-converter>=0.7,<0.8',
                                       'openpyxl>=3.0.10,<4.0.0'],
 ':extra == "test" or extra == "dev"': ['pytest>=7.1.2,<8.0.0',
                                        'pytest-cov>=3.0.0,<4.0.0'],
 ':extra == "test" or extra == "dev" or extra == "doc"': ['pandas>=1.4,<2.0']}

setup_kwargs = {
    'name': 'bblocks',
    'version': '0.1.1',
    'description': 'A package with tools to download and analyse international development data.',
    'long_description': '# bblocks\n\n\n[![pypi](https://img.shields.io/pypi/v/bblocks.svg)](https://pypi.org/project/bblocks/)\n[![python](https://img.shields.io/pypi/pyversions/bblocks.svg)](https://pypi.org/project/bblocks/)\n[![codecov](https://codecov.io/gh/ONECampaign/bblocks/branch/main/graphs/badge.svg)](https://codecov.io/github/ONECampaign/bblocks)\n\n\n\nA package with tools to download and analyse international development data.\n\n\n* Documentation: <https://ONECampaign.github.io/bblocks>\n* GitHub: <https://github.com/ONECampaign/bblocks>\n* PyPI: <https://pypi.org/project/bblocks/>\n* Free software: MIT\n\n\n## Features\n\n* TODO\n',
    'author': 'The ONE Campaign',
    'author_email': 'data@one.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ONECampaign/bblocks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
