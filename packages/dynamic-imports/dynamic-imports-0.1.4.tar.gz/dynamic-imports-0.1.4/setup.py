# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dynamic_imports',
 'dynamic_imports.tests',
 'dynamic_imports.tests.test_pkg',
 'dynamic_imports.tests.test_pkg.l1_1',
 'dynamic_imports.tests.test_pkg.l1_2',
 'dynamic_imports.tests.test_pkg.l1_2.l2_1']

package_data = \
{'': ['*']}

install_requires = \
['ready-logger>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'dynamic-imports',
    'version': '0.1.4',
    'description': 'Dynamic discovery and importing.',
    'long_description': None,
    'author': 'Dan Kelleher',
    'author_email': 'dan@danklabs.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
