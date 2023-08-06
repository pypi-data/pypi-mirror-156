# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgperf']

package_data = \
{'': ['*'], 'pgperf': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'SQLAlchemy>=1.4.36,<2.0.0',
 'XlsxWriter>=3.0.3,<4.0.0',
 'fire>=0.4.0,<0.5.0',
 'numpy>=1.22.4,<2.0.0',
 'omegaconf>=2.2.1,<3.0.0',
 'pandas>=1.4.2,<2.0.0',
 'psycopg2>=2.9.3,<3.0.0',
 'rich>=12.4.4,<13.0.0',
 'tabulate>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['pgperf = pgperf.main:run']}

setup_kwargs = {
    'name': 'pgperf',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Aldo A. Villagra B.',
    'author_email': 'aldovillagra@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
