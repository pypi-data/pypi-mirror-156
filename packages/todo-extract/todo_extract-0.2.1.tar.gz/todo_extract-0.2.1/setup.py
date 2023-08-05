# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['todo_extract']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'todo-extract',
    'version': '0.2.1',
    'description': 'Extract TODO items from the text file',
    'long_description': None,
    'author': 'Krystian Safjan',
    'author_email': 'ksafjan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
