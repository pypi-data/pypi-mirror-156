# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datapeek', 'datapeek.src.logger', 'datapeek.src.peeker']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'datapeek',
    'version': '0.1.0',
    'description': 'A python package to display data in a more fluent and well formatted manner using colours and smart formatting',
    'long_description': None,
    'author': 'lsmucassi',
    'author_email': 'lindasmucassi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
