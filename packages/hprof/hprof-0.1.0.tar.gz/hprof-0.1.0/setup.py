# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hprof']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hprof',
    'version': '0.1.0',
    'description': 'Analyse and explore .hprof heap dumps',
    'long_description': None,
    'author': 'Snild Dolkow',
    'author_email': 'snild@dolkow.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
