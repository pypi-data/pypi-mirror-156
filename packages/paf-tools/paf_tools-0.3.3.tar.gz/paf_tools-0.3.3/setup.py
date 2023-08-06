# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paf_tools',
 'paf_tools.generators',
 'paf_tools.generators.data.addresses',
 'paf_tools.generators.data.email',
 'paf_tools.generators.data.names',
 'paf_tools.os',
 'paf_tools.sap',
 'paf_tools.text']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'pymssql>=2.2.5,<3.0.0', 'xmltodict>=0.13.0,<0.14.0']

setup_kwargs = {
    'name': 'paf-tools',
    'version': '0.3.3',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
