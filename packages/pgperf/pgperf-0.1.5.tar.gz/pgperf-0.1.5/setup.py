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
    'version': '0.1.5',
    'description': 'PostgreSQL Performance Tools',
    'long_description': '# Python PostgreSQL Performance Tools\n\nPython port of [Heroku PG Extras](https://github.com/heroku/heroku-pg-extras) with several additions and improvements. The goal of this project is to provide powerful insights into the PostgreSQL database for Python apps that are not using the Heroku PostgreSQL plugin.\n\nQueries can be used to obtain information about a Postgres instance, that may be useful when analyzing performance issues. This includes information about locks, index usage, buffer cache hit ratios and vacuum statistics. Python API enables developers to easily integrate the tool into e.g. automatic monitoring tasks.\n\nYou can check out this blog post for detailed step by step tutorial on how to [optimize PostgreSQL using PG Extras library](https://pawelurbanek.com/postgresql-fix-performance).\n\nAlternative versions:\n\n- [Ruby](https://github.com/pawurb/ruby-pg-extras)\n\n- [Ruby on Rails](https://github.com/pawurb/rails-pg-extras)\n\n- [NodeJS](https://github.com/pawurb/node-postgres-extras)\n\n- [Elixir](https://github.com/pawurb/ecto_psql_extras)\n\n- [Haskell](https://github.com/pawurb/haskell-pg-extras)',
    'author': 'Aldo A. Villagra B.',
    'author_email': 'aldovillagra@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aldovillagra/pgperf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
