# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['merkly', 'merkly.utils']

package_data = \
{'': ['*']}

install_requires = \
['pysha3>=1.0.2,<2.0.0']

setup_kwargs = {
    'name': 'merkly',
    'version': '0.4.2',
    'description': '🌳 The simple and easy implementation of Merkle Tree',
    'long_description': "# 🌳 Merkly\n\nThe **simple and easy** implementation of **Python Merkle Tree**\n\n---\n\n[![Test](https://github.com/olivmath/merkly/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/olivmath/merkly/actions/workflows/test.yml)\n![GitHub last commit](https://img.shields.io/github/last-commit/olivmath/merkly)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/olivmath/merkly)\n\n[![PyPI](https://img.shields.io/pypi/v/merkly)](https://pypi.org/project/merkly/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/merkly)](https://pypi.org/project/merkly/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/merkly)](https://pypi.org/project/merkly/)\n![PyPI - License](https://img.shields.io/pypi/l/merkly)\n\n## Table of Contents\n\n- [Credits](#credits)\n- [How to install](#how-to-install)\n- [How to works](#how-to-works)\n- [How to use](#how-to-use)\n- [Contributing](#contributing)\n- [License](#license)\n\n## Credits\n\n[![GitHub Contributors Image](https://contrib.rocks/image?repo=olivmath/merkly)](https://github.com/olivmath/merkly/graphs/contributors)\n\n## How to install\n\n```\npoetry add merkly\n```\n\n```\npip install merkly\n```\n\n## How it works\n\nThis library provides a clean and easy to use implementation of the Merkle Tree with the following features:\n\n- [x] Create Leaf\n- [x] Create Root\n- [ ] Create Proof\n- [ ] Validate Leafs\n\n![Merkle Tree](assets/merkle-tree.png)\n\n## How to Use\n\nCreate a Merkle Tree\n\n```python\nfrom merkly.mtree import MerkleTree\n\nmtree = MerkleTree(\n  ['a', 'b', 'c', 'd']\n)\n\nassert mtree.leafs == [\n  '3ac225168df54212a25c1c01fd35bebfea408fdac2e31ddd6f80a4bbf9a5f1cb',\n  'b5553de315e0edf504d9150af82dafa5c4667fa618ed0a6f19c69b41166c5510',\n  '0b42b6393c1f53060fe3ddbfcd7aadcca894465a5a438f69c87d790b2299b9b2',\n  'f1918e8562236eb17adc8502332f4c9c82bc14e19bfc0aa10ab674ff75b3d2f3'\n]\n\nassert mtree.root == [\n  '115cbb4775ed495f3d954dfa47164359a97762b40059d9502895def16eed609c'\n]\n```\n\n## Contributing\n\n- Before read a code of conduct: **[CODE_OF_CONDUCT](CODE_OF_CONDUCT.md)**\n- Follow the guide of development: **[CONTRIBUTING](CONTRIBUTING.md)**\n\n## License\n\n[MIT](LICENSE)\n",
    'author': 'Lucas Oliveira',
    'author_email': 'olivmath@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/olivmath/merkly.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
