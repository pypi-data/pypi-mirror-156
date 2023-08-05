# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['swaggyp', 'swaggyp.tests']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'valley>=1.5.6,<2.0.0']

setup_kwargs = {
    'name': 'swaggyp',
    'version': '0.3.0',
    'description': 'Python library for generating Swagger templates based on valley',
    'long_description': None,
    'author': 'Brian Jinwright',
    'author_email': 'bjinwright@qwigo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
