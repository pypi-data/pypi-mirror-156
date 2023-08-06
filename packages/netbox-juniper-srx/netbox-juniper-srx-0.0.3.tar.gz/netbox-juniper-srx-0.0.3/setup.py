# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netbox_juniper_srx',
 'netbox_juniper_srx.api',
 'netbox_juniper_srx.migrations']

package_data = \
{'': ['*'], 'netbox_juniper_srx': ['templates/netbox_juniper_srx/*']}

setup_kwargs = {
    'name': 'netbox-juniper-srx',
    'version': '0.0.3',
    'description': 'Netbox plugin to manage Juniper SRX security configuration objects.',
    'long_description': None,
    'author': 'Calvin Remsburg',
    'author_email': 'cremsburg.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
