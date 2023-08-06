# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['colang']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'colang',
    'version': '0.0.1',
    'description': 'Clean, intuitive, and powerful modeling language for Conversational AI.',
    'long_description': None,
    'author': 'Razvan Dinu',
    'author_email': 'razvan@colang.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
