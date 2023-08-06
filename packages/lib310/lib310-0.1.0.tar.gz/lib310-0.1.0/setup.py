# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['b10', 'b10.data', 'b10.machinelearning', 'b10.tools', 'b10.visualization']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.79,<2.0',
 'google-cloud-bigquery>=3.2.0,<4.0.0',
 'google-cloud>=0.34.0,<0.35.0']

setup_kwargs = {
    'name': 'lib310',
    'version': '0.1.0',
    'description': 'b10 Python Package',
    'long_description': None,
    'author': 'naghipourfar',
    'author_email': 'naghipourfar@berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.7,<3.11',
}


setup(**setup_kwargs)
