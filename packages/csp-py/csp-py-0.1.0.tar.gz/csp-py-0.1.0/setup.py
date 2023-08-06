# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['csp_py']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'csp-py',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'cilanthr0',
    'author_email': 'cilanthr0@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
