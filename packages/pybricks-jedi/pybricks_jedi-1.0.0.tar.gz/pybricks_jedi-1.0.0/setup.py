# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pybricks_jedi']

package_data = \
{'': ['*']}

install_requires = \
['jedi>=0.18.1,<0.19.0',
 'pybricks>=3.2.0b1-r2,<4.0.0',
 'typing-extensions>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'pybricks-jedi',
    'version': '1.0.0',
    'description': 'Code completion for Pybricks.',
    'long_description': None,
    'author': 'The Pybricks Authors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
