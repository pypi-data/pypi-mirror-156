# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['algoworld_contracts',
 'algoworld_contracts.auction',
 'algoworld_contracts.auction.helpers',
 'algoworld_contracts.common',
 'algoworld_contracts.swapper']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML==6.0', 'py-algorand-sdk==1.13.1', 'pyteal==0.10.0']

setup_kwargs = {
    'name': 'algoworld-contracts',
    'version': '1.3.6',
    'description': 'AlgoWorld Smart Contracts and Signatures',
    'long_description': '<p align="center"><a  href="https://twitter.com/algoworld_nft/status/1450608110268211203"><img  width=100%  src="https://i.imgur.com/cGWGmxa.png"  alt="687474703a2f2f6936332e74696e797069632e636f6d2f333031336c67342e706e67"  border="0" /></a></p>\n\n<p align="center">\n    <a href="https://algorand.com"><img src="https://img.shields.io/badge/Powered by-Algorand-blue.svg" /></a>\n    <a href="https://algoworld.io"><img src="https://img.shields.io/badge/AlgoWorld-Website-pink.svg" /></a>\n    <a href="https://algoworldexplorer.io"><img src="https://img.shields.io/badge/AlgoWorldExplorer-Platform-red.svg" /></a>\n    <a><img src="https://visitor-badge.glitch.me/badge?page_id=AlgoWorldNFT.algoworld-contracts&right_color=green" /></a>\n    <a href="https://github.com/AlgoWorldNFT/algoworld-contracts/actions/workflows/ci.yaml"><img src="https://github.com/AlgoWorldNFT/algoworld-contracts/actions/workflows/ci.yaml/badge.svg" /></a>\n    <a href="https://codecov.io/gh/AlgoWorldNFT/algoworld-contracts"><img src="https://codecov.io/gh/AlgoWorldNFT/algoworld-contracts/branch/main/graph/badge.svg?token=2O1VAOJCUD"  /></a>\n</p>\n\n## 📃 About\n\nThe following repository hosts the source codes for:\n- `AlgoWorld Swapper`\'s algorand smart signatures.\n- `AlgoWorldExplorer`\'s stateful smart contracts for card auctions and card trading. Modified version of [OpenNFT](https://github.com/ulamlabs/OpenNFT)\'s smart contracts.\n\n_**⚠️ NOTE: These contracts are not formally audited by accredited third parties. However, contracts are a basis for certain functionality on the AlgoWorldExplorer.io platform and were created in collaboration with Solution Architect from Algorand (credits @cusma). Code is provided under MIT license.**_\n\n## Prerequisites\n\n-   [poetry](https://python-poetry.org/)\n-   [pre-commit](https://pre-commit.com/)\n-   [Algorand Sandbox](https://github.com/algorand/sandbox)\n-   [Docker](https://www.docker.com/)\n\n## 🚀 Overview\n\nAlgoWorld currently offers stateful contracts used for auction trading on AlgoWorldExplorer and several smart signatures used for swapping on AlgoWorld Swapper.\n\n---\n\nIf you are looking to install algoworld contracts into your project run the following command:\n\n```bash\npip install algoworld-contracts\n```\n\n### Example usage\n\n```python\nfrom algoworld_contracts import contracts\n\n# Replace inputParams with real values\nasa_to_asa_swap = contracts.get_swapper_teal(\n        inputParams.creator_address,\n        inputParams.offered_asa_id,\n        inputParams.offered_asa_amount,\n        inputParams.requested_asa_id,\n        inputParams.requested_asa_amount,\n        inputParams.incentive_wallet,\n        inputParams.incentive_fee,\n    )\n\n# asa_to_asa_swap is a string of TEAL code\nresponse = algod.compile(asa_to_asa_swap)\n...\n```\n\n### Swapper\n\nThere are two main types of smart signatures available:\n\n- [ASA to ASA swap | 🎴↔️🎴](algoworld_contracts/swapper/asa_to_asa_swapper.py):  Smart signature that allows performing a swap of any single ASA of specified amount to any other single ASA of specified amount.\n- - [Swap Configuration Proxy 📝](algoworld_contracts/swapper/swap_proxy.py): Smart signature that powers the [AlgoWorld Swapper](https://swapper.algoworld.io) by allowing users to issue certain transactions that contain links to swap configuration files stored as `.json` files on `ipfs`. Proxy is then used to obtain those `ipfs` files by grabbing the latest pay transaction using Algorand Indexer queries.\n\n- [ASAs to ALGO swap | 🎴🎴🎴↔️💰](algoworld_contracts/swapper/asas_to_algo_swapper.py): Smart signature that allows performing a swap of multiple ASAs of specified amount to ALGO of specified amount.\n\n### Auction\n\nA set of stateful smart contracts for card auctions and card trading:\n- [ASAs for ALGO with trades and bidding | 🎴💰🔨](src/auction/manager.py): <br> Allows trading ASA via auctions, selling or purchasing directly.\n\n## ⚙️ Installation\n\nThis section assumes that poetry and pre-commit are installed and executed from the root folder of this repository.\n\n1. Clone the repo\n\n```bash\ngit clone https://github.com/AlgoWorldNFT/algoworld-contracts\n```\n\n2. Install python requirements\n\n```bash\npoetry install # install all dependencies\npoetry shell # activate virtual env\n```\n\n(OPTIONAL) 3. Configure `pre-commit` hooks\n\n```bash\npre-commit install\n```\n\nIf you are not going to setup `pre-commit` locally, there is a Github Actions plugin that will autoformat your branch if you are opening a PR with commits that contain un-formatted code.\n\n## 🧪 Testing\n\nTesting assumes that docker-compose is installed and available. Project is relying on `pytest-docker-compose` plugin that automatically boots up temporary algorand sandbox and destroys the containers after the tests are finished.\n\n```bash\n(.venv) pytest\n```\n\nYou can also include `[pytest]` into your commit message to trigger the test in CI pipeline on `push` action (on pr it is triggered automatically).\n\n## 🚧 Contribution guideline\n\nSee [`CONTRIBUTING.md`](CONTRIBUTING.md)\n\n## ⭐️ Stargazers\n\nSpecial thanks to everyone who forked or starred the repository ❤️\n\n[![Stargazers repo roster for @AlgoWorldNFT/algoworld-contracts](https://reporoster.com/stars/dark/AlgoWorldNFT/algoworld-contracts)](https://github.com/AlgoWorldNFT/algoworld-contracts/stargazers)\n\n[![Forkers repo roster for @AlgoWorldNFT/algoworld-contracts](https://reporoster.com/forks/dark/AlgoWorldNFT/algoworld-contracts)](https://github.com/AlgoWorldNFT/algoworld-contracts/network/members)\n',
    'author': 'AlgoWorld',
    'author_email': 'info@algoworld.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AlgoWorldNFT/algoworld-contracts',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
