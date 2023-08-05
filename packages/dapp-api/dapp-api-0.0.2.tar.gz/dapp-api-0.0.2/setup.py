# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dapp_api', 'dapp_api.fragments', 'dapp_api.queries']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0',
 'sgqlc>=16.0,<17.0',
 'tqdm>=4.63.1,<5.0.0',
 'wheel>=0.36.2,<0.37.0']

extras_require = \
{'data-tools': ['jupyterlab>=3.0.0,<4.0.0',
                'ipywidgets>=7.6.3,<8.0.0',
                'pandas>=1.4.1,<2.0.0',
                'numpy>=1.22.3,<2.0.0'],
 'docs': ['mkdocs-material>=8.2.9,<9.0.0',
          'mkdocstrings>=0.18.1,<0.19.0',
          'mkdocs-jupyter>=0.20.1,<0.21.0'],
 'web3': ['web3>=5.28.0,<6.0.0']}

setup_kwargs = {
    'name': 'dapp-api',
    'version': '0.0.2',
    'description': "Golden's Python wrapper for the dApp GraphQL API",
    'long_description': None,
    'author': 'aychang95',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
