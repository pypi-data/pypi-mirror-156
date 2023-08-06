# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edval2mb', 'edval2mb.cli']

package_data = \
{'': ['*']}

install_requires = \
['click-config-file>=0.6.0,<0.7.0',
 'click>=8.1.3,<9.0.0',
 'pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'edval2mb',
    'version': '0.3.0',
    'description': 'Convert edval export to ManageBac CSV upload for timetables',
    'long_description': None,
    'author': 'Adam Morris',
    'author_email': 'classroomtechtools.ctt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
