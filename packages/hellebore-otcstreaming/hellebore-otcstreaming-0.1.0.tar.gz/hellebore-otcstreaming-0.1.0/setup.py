# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hellebore_otcstreaming']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'twine>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'hellebore-otcstreaming',
    'version': '0.1.0',
    'description': 'API Wrapper for the ISDA calculator of OTCStreaming.',
    'long_description': None,
    'author': 'Benjamin Denise',
    'author_email': 'bdenise@helleboretech.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
