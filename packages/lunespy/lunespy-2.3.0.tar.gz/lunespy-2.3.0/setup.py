# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lunespy',
 'lunespy.client.transactions',
 'lunespy.client.transactions.alias',
 'lunespy.client.transactions.burn',
 'lunespy.client.transactions.cancel_lease',
 'lunespy.client.transactions.lease',
 'lunespy.client.transactions.mass',
 'lunespy.client.transactions.reissue',
 'lunespy.crypto',
 'lunespy.server.address',
 'lunespy.server.blocks',
 'lunespy.server.nodes',
 'lunespy.server.transactions',
 'lunespy.tx.issue',
 'lunespy.tx.sponsor',
 'lunespy.tx.transfer',
 'lunespy.utils',
 'lunespy.wallet']

package_data = \
{'': ['*']}

install_requires = \
['base58>=2.1.0,<3.0.0',
 'httpx>=0.22.0,<0.23.0',
 'pydantic>=1.9.0,<2.0.0',
 'pysha3>=1.0.2,<2.0.0',
 'python-axolotl-curve25519>=0.4.1.post2,<0.5.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'lunespy',
    'version': '2.3.0',
    'description': '📦 Library for communication with nodes in mainnet or testnet of the lunes-blockchain network Allows the automation of sending assets, issue end reissue tokens, leasing, registry, and create new wallet.',
    'long_description': '# LunesPy\n\n📦 Library for communication with nodes in mainnet or testnet of the lunes-blockchain network Allows the automation of sending assets, issue end reissue tokens, leasing, registry, and create new wallet.\n\n[![CodeQL](https://github.com/lunes-platform/lunespy/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/lunes-platform/lunespy/actions/workflows/codeql-analysis.yml)\n[![Test](https://github.com/lunes-platform/lunespy/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/lunes-platform/lunespy/actions/workflows/test.yml)\n![PyPI](https://img.shields.io/pypi/v/lunespy)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lunespy)\n\n![PyPI - Downloads](https://img.shields.io/pypi/dm/lunespy)\n![GitHub last commit](https://img.shields.io/github/last-commit/lunes-platform/lunespy)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/lunes-platform/lunespy)\n\n![PyPI - License](https://img.shields.io/pypi/l/lunespy)\n![Discord](https://img.shields.io/discord/958424925453058158)\n\n---\n\n## Table of Contents\n\n- [Credits](#credits)\n- [How to install](#how-to-install)\n- [How it works](#how-it-works)\n- [Contributing](#contributing)\n- [License](#license)\n\n## Credits\n\n[![GitHub Contributors Image](https://contrib.rocks/image?repo=lunes-platform/lunespy)](https://github.com/lunes-platform/lunespy/graphs/contributors)\n\n## How to install\n\n```\npip install lunespy\n```\n\n```\npoetry add lunespy\n```\n\n## How it works\n\n- see the docs: [Telescope](https://lunes-platform.github.io/telescope)\n\n## Contributing\n\n- Before read a code of conduct: **[CODE_OF_CONDUCT](CODE_OF_CONDUCT.md)**\n- Follow the guide of development: **[CONTRIBUTING](CONTRIBUTING.md)**\n\n## License\n\n[Apache v2.0](LICENSE)\n',
    'author': 'Lunes Platform',
    'author_email': 'development@lunes.io',
    'maintainer': 'Lucas Oliveira',
    'maintainer_email': 'olivmath@protonmail.com',
    'url': 'https://github.com/lunes-platform/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
