# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gator', 'gator.models']

package_data = \
{'': ['*']}

install_requires = \
['flask-mongoengine>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'gator-models',
    'version': '0.1.0',
    'description': 'MongoDB models for Gator API',
    'long_description': None,
    'author': 'Shon Verch',
    'author_email': 'verchshon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
