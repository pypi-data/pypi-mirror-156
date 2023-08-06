# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crypto_exchange_handler']

package_data = \
{'': ['*']}

install_requires = \
['python-binance>=1.0.16,<2.0.0']

setup_kwargs = {
    'name': 'crypto-exchange-handler',
    'version': '0.0.5',
    'description': 'This package provides template class and its implementations to handle crypto exchanges in unified way.',
    'long_description': '# crypto_exchange_handler [![Total alerts](https://img.shields.io/lgtm/alerts/g/crypto-ralph/crypto_exchange_handler.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/crypto-ralph/crypto_exchange_handler/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/crypto-ralph/crypto_exchange_handler.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/crypto-ralph/crypto_exchange_handler/context:python)\n\nThis library provides classes which can be used to access cryptocurrency exchanges from your code with unified manner.\n\n# License \n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n\nFor the details refer to LICENSE.md\n',
    'author': 'CryptoRalph',
    'author_email': 'doxter@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
