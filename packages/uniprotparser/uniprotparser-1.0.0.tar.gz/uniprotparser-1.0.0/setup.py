# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uniprotparser']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.0,<3.0.0']

setup_kwargs = {
    'name': 'uniprotparser',
    'version': '1.0.0',
    'description': 'Getting Uniprot Data from Uniprot Accession ID through Uniprot REST API',
    'long_description': None,
    'author': 'Toan Phung',
    'author_email': 'toan.phungkhoiquoctoan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
