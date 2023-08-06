# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pecs_framework', 'pecs_framework.internals']

package_data = \
{'': ['*']}

install_requires = \
['deepmerge>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'pecs-framework',
    'version': '1.0.1',
    'description': 'The ✨Respectably Muscled✨ Python Entity Component System',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
