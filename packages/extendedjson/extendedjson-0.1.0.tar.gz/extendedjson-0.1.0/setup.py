# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['extendedjson']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'extendedjson',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Rodrigo Girão Serrão',
    'author_email': '5621605+RodrigoGiraoSerrao@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
