# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shipout', 'shipout.infra_utils']

package_data = \
{'': ['*']}

install_requires = \
['azure-identity>=1.10.0,<2.0.0',
 'azure-mgmt-authorization>=2.0.0,<3.0.0',
 'azure-mgmt-resource>=21.1.0,<22.0.0',
 'azure-mgmt-storage>=20.0.0,<21.0.0',
 'docker>=5.0.3,<6.0.0',
 'pulumi-azure-native>=1.64.1,<2.0.0',
 'pulumi-azure>=5.10.0,<6.0.0',
 'pulumi>=3.33.1,<4.0.0',
 'typer[all]>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['shipout = shipout.main:app']}

setup_kwargs = {
    'name': 'shipout',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'BlurwareAdmin',
    'author_email': 'admin@blurware.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
