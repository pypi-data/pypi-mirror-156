# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['date_format_machine']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click-log>=0.4.0,<0.5.0',
 'click>=8.1.3,<9.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'tabulate>=0.8.10,<0.9.0']

entry_points = \
{'console_scripts': ['date_format_machine = date_format_machine.dfm:cli',
                     'dfm = date_format_machine.dfm:cli']}

setup_kwargs = {
    'name': 'date-format-machine',
    'version': '0.9',
    'description': 'Tool for manipulating date strings',
    'long_description': None,
    'author': 'Ryan',
    'author_email': 'citizen.townshend@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
