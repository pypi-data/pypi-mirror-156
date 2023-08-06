# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kafka_schema_registry_admin']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0', 'requests>=2.28.0,<3.0.0']

setup_kwargs = {
    'name': 'kafka-schema-registry-admin',
    'version': '0.2.0',
    'description': 'Pure HTTP client to manage schemas in Schema Registry',
    'long_description': None,
    'author': 'John Preston',
    'author_email': 'john@ews-network.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
