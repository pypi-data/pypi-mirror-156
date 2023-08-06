# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neural_best_buddies',
 'neural_best_buddies.algorithms',
 'neural_best_buddies.models',
 'neural_best_buddies.options',
 'neural_best_buddies.util']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'neural-best-buddies',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
