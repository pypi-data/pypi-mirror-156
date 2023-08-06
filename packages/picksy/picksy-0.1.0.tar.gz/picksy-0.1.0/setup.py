# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['picksy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'picksy',
    'version': '0.1.0',
    'description': 'Picksy. Python picker module with a simple search.',
    'long_description': None,
    'author': 'Paul Glushak (hxii)',
    'author_email': 'paul@glushak.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
