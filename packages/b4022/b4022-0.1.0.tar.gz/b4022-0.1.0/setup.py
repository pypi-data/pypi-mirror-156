# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['b4022']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0.5,<5.0.0', 'requests>=2.28.0,<3.0.0']

setup_kwargs = {
    'name': 'b4022',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Aisten',
    'author_email': 'gvilkson@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
