# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['multisig_ci']

package_data = \
{'': ['*']}

install_requires = \
['ape_safe==0.5.0',
 'eth_brownie==1.19',
 'psutil==5.9.1',
 'requests==2.27.1',
 'safe-eth-py==4.0.1',
 'tenacity==8.0.1']

setup_kwargs = {
    'name': 'multisig-ci',
    'version': '0.3.3',
    'description': 'Gnosis safe ci scripts.',
    'long_description': None,
    'author': 'kx9x',
    'author_email': 'kx9x@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
