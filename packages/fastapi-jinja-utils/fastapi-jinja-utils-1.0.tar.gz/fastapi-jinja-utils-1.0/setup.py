# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_jinja_utils']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0', 'fastapi>=0.78.0,<0.79.0']

setup_kwargs = {
    'name': 'fastapi-jinja-utils',
    'version': '1.0',
    'description': '',
    'long_description': None,
    'author': 'Tyler M Kontra',
    'author_email': 'tyler@tylerkontra.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
