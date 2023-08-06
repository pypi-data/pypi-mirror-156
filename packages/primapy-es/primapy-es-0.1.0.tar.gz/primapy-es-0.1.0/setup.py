# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['primapy_es']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'primapy-es',
    'version': '0.1.0',
    'description': 'Safety placeholder',
    'long_description': None,
    'author': 'Riccardo Sayn',
    'author_email': 'riccardo.sayn@prima.it',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
