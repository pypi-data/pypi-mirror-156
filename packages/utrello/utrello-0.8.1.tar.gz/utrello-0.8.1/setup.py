# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['utrello']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.3,<2.0.0', 'requests>=2.28.0,<3.0.0']

entry_points = \
{'console_scripts': ['utrello = utrello:main']}

setup_kwargs = {
    'name': 'utrello',
    'version': '0.8.1',
    'description': '',
    'long_description': None,
    'author': 'Davi Koscianski Vidal',
    'author_email': 'davividal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
