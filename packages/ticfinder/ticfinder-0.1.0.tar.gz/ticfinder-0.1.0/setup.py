# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ticfinder']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=5.1,<6.0',
 'astroquery>=0.4.6,<0.5.0',
 'mkdocs-include-markdown-plugin>=3.4.0,<4.0.0',
 'mkdocstrings-python>=0.7.1,<0.8.0',
 'numpy>=1.23.0,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'ticgen>=1.0.4,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'ticfinder',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Christina Hedges',
    'author_email': 'christina.l.hedges@nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
