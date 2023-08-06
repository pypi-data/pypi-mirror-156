# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clearsoda']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'clearsoda',
    'version': '0.0.2',
    'description': 'Library to generate scratch projects using object-oriented relations.',
    'long_description': '# clearsoda\nclearsoda is a library for generating scratch projects in python\n',
    'author': 'xAspirus',
    'author_email': 'movxa@protonmail.com',
    'maintainer': 'xAspirus',
    'maintainer_email': 'movxa@protonmail.com',
    'url': 'https://github.com/xAspirus/clearsoda',
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
