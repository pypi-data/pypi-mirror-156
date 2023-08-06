# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pls_cli', 'pls_cli.utils']

package_data = \
{'': ['*']}

modules = \
['README']
install_requires = \
['rich>=12.4.4,<13.0.0', 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['pls = pls_cli.please:app']}

setup_kwargs = {
    'name': 'pls-cli',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Felipe Guedes',
    'author_email': 'contatofelipeguedes@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/guedesfelipe/pls-cli',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
