# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hoppr',
 'hoppr.base_plugins',
 'hoppr.configs',
 'hoppr.core_plugins',
 'hoppr.types',
 'hoppr.types.cyclonedx_1_3',
 'hoppr.types.cyclonedx_1_4']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click==8.1.3',
 'cyclonedx-python-lib>=2.0.0,<3.0.0',
 'jsonschema>=4.4.0,<5.0.0',
 'packageurl-python>=0.9.9,<0.10.0',
 'pydantic[email]>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'typer>=0.4.0,<0.5.0',
 'types-PyYAML>=6.0.5,<7.0.0',
 'urllib3>=1.26.9,<2.0.0']

entry_points = \
{'console_scripts': ['hopctl = hoppr.main:app']}

setup_kwargs = {
    'name': 'hoppr',
    'version': '0.18.2',
    'description': 'A tool for defining, verifying, and transferring software dependencies between environments.',
    'long_description': None,
    'author': 'LMCO Open Source',
    'author_email': 'open.source@lmco.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/lmco/hoppr/hoppr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
