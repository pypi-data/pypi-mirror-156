# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hellebore_otcstreaming']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'hellebore-otcstreaming',
    'version': '0.1.1',
    'description': 'API Wrapper for OTCStreaming.',
    'long_description': '# Hellebore OtcStreaming\n\nAPI Wrapper for the [OTCStreaming](https://www.otcstreaming.com/)\'API.\n\n## Features :\n- ISDA Calculator on the base of the [OTCStraming\'s calculator](https://www.otcstreaming.com/calculator)\n\n\n## Installation\n\n```sh\npip install ...\n```\n\n## Usage\n\n### ISDA Calculator\n\nIn order to get ISDA prices for the index `ITXEB536` :\n \n```python\nfrom hellebore_otcstreaming import isda_calculator, ProductInfo\n\nticker = ProductInfo.from_mnemonic("ITXEB535", "2022-05-01")\n\nprices = isda_calculator(ticker, "2022-05-01", price = 10)\n```\n`prices` is a dict holding values of several price types :\n```json\n{"cashAmount": 38144.17450850366,\n "isdaInterestCurve": "02-May-2022 EUR",\n "prices": {"CS01": 4.23495037684285,\n            "DirtyUpfront": -3.8144174508503657,\n            "FullUpfront": 0.410861198242655,\n            "Price": 103.6977507841837,\n            "RiskyBp": 4.108611982426353,\n            "Spread": 10.0,\n            "Upfront": -3.697750784183699}}\n```\n',
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
