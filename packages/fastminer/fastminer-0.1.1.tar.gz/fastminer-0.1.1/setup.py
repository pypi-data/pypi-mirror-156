# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastminer', 'fastminer.fast', 'fastminer.spmf']

package_data = \
{'': ['*'], 'fastminer': ['jars/*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0', 'pyjnius>=1.4.1,<2.0.0']

setup_kwargs = {
    'name': 'fastminer',
    'version': '0.1.1',
    'description': 'fast data mining algos',
    'long_description': None,
    'author': 'Tony',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
