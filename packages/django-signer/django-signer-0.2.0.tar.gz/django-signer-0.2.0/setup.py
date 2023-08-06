# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_signer',
 'django_signer.core',
 'django_signer.test',
 'django_signer.utils']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=7.1.2,<8.0.0']

setup_kwargs = {
    'name': 'django-signer',
    'version': '0.2.0',
    'description': 'A lightweight implementation of a signer based on Django TimestampSigner.',
    'long_description': None,
    'author': 'Natan Lima Viana',
    'author_email': 'natanvianat16@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
