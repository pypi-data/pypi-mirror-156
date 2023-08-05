# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['msekzper']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'msekzper',
    'version': '0.9.7',
    'description': 'rabotay molu',
    'long_description': None,
    'author': 'NuatStanskiy',
    'author_email': 'smiril13@mail.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
