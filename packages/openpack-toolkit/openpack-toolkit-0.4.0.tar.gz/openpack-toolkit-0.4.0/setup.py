# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openpack_toolkit',
 'openpack_toolkit.activity',
 'openpack_toolkit.bin',
 'openpack_toolkit.codalab',
 'openpack_toolkit.codalab.operation_segmentation',
 'openpack_toolkit.configs',
 'openpack_toolkit.configs.datasets',
 'openpack_toolkit.data',
 'openpack_toolkit.download',
 'openpack_toolkit.utils']

package_data = \
{'': ['*']}

install_requires = \
['numpy<1.22.0',
 'omegaconf>=2.2.2,<3.0.0',
 'pandas>=1.2.4',
 'scipy>=1.7.3,<2.0.0',
 'sklearn>=0.0']

entry_points = \
{'console_scripts': ['optk-download = '
                     'openpack_toolkit.bin.download:entry_func']}

setup_kwargs = {
    'name': 'openpack-toolkit',
    'version': '0.4.0',
    'description': 'Toolkit for OpenPack Dataset',
    'long_description': '# OpenPack Dataset Toolkit (optk)\n\n![OpenPack Challenge Logo](./img/OpenPackCHALLENG-black.png)\n\n[![Test](https://github.com/open-pack/openpack-toolkit/actions/workflows/test.yaml/badge.svg)](https://github.com/open-pack/openpack-toolkit/actions/workflows/test.yaml)\n[![API Docs - GitHub Pages](https://github.com/open-pack/openpack-toolkit/actions/workflows/deploy-docs.yaml/badge.svg)](https://github.com/open-pack/openpack-toolkit/actions/workflows/deploy-docs.yaml)\n\n"OpenPack Dataset" is a new large-scale multi modal dataset of manual packing process.\nOpenPack is an open access logistics-dataset for human activity recognition, which contains human movement and package information from 16 distinct subjects.\nThis repository provide utilities to explore our exciting dataset.\n\n## Install\n\nWe provide some utility functions as python package. You can install via pip with the following command.\n\n```bash\n# Pip\npip install openpack-toolkit\n\n# Poetry\npoetry add  openpack-toolkit\n```\n\n## Docs & Links\n\n### Tool\n\n- [API Docs](https://open-pack.github.io/openpack-toolkit/openpack_toolkit/)\n- [PyPI](https://pypi.org/project/openpack-toolkit/)\n\n### Dataset\n\n- [Homepage](https://open-pack.github.io/) (External Site)\n- [Subjects & Recording Scenarios](./docs/USER.md)\n- [Activity Class Definition](./docs/ANNOTATION.md)\n- [Modality](./docs/DATA_STREAM.md)\n- [Data Split (Train/Val/Test/Submission)](./docs/DATA_SPLIT.md)\n\n### Task\n\n- Work Operation Recognition\n  - [OpenPack Challenge](./docs/OPENPACK_CHALLENGE/)\n\n## Examples (PyTorch)\n\nPyTorch code samples for work operation prediction task is available.\nSee [openpack-torch](https://github.com/open-pack/openpack-torch) for more dietail.\n\n- [U-Net with Accelration Data](https://github.com/open-pack/openpack-torch/tree/main/examples/unet)\n- [ST-GCN with Keypoints Data](https://github.com/open-pack/openpack-torch/tree/main/examples/st-gcn)\n\n## Download Dataset\n\n```bash\noptk-download -d ../data/datasets -v v0.2.0 -s atr-qags,openpack-operations\n\n# If you are a user of poetry,\npoetry run optk-download -d ../data/datasets -v v0.2.0 -s atr-qags,openpack-operations\n```\n\nHelp:\n\n```bash\n$ poetry run optk-download -d ../data/datasets -h\nusage: optk-download [-h] -d DATASET_DIR [-v VERSION] [-s STREAMS]\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -d DATASET_DIR, --dataset-dir DATASET_DIR\n                        Path to dataset directory. Downloaded data will be stored under the directory\n  -v VERSION, --version VERSION\n                        Target dataset version. Default: v0.2.0\n  -s STREAMS, --streams STREAMS\n                        A list of data stream names that you want to download. Stream names must be separated by commas. Defaul: atr-qags,openpack-operations\n```\n\n### Dataset Structure\n\n[v0.2.0](https://zenodo.org/record/6697990)\n\n```txt\n../data/datasets/\n└── openpack\n    └── v0.2.0\n        ├── U0102\n        │   ├── annotation\n        │   │   └── openpack-operations\n        │   │       ├── S0100.csv\n        │   │       ├── S0200.csv\n        │   │       ├── S0300.csv\n        │   │       ├── S0400.csv\n        │   │       └── S0500.csv\n        │   ├── atr\n        │   │   ├── atr01\n        │   │   │   ├── S0100.csv\n        │   │   │   ├── S0200.csv\n        │   │   │   ├── S0300.csv\n        │   │   │   ├── S0400.csv\n        │   │   │   └── S0500.csv\n        │   │   ├── atr02\n        │   │   │   ├── S0100.csv\n        │   │   │   ├── S0200.csv\n        │   │   │   ├── S0300.csv\n        │   │   │   ├── S0400.csv\n        │   │   │   └── S0500.csv\n        │   │   ├── atr03\n        │   │   │   ├── S0100.csv\n        │   │   │   ├── S0200.csv\n        │   │   │   ├── S0300.csv\n        │   │   │   ├── S0400.csv\n        │   │   │   └── S0500.csv\n        │   │   └── atr04\n        │   │       ├── S0100.csv\n        │   │       ├── S0200.csv\n        │   │       ├── S0300.csv\n        │   │       ├── S0400.csv\n        │   │       └── S0500.csv\n        │   └── kinect\n        │       └── 2d-kpt\n        │           └── mmpose-hrnet-w48-posetrack18-384x288-posewarper-stage2\n        │               ├── U0102\n        │               │   └── single\n        │               │       ├── S0100.json\n        │               │       ├── S0200.json\n        │               │       ├── S0300.json\n        │               │       ├── S0400.json\n        │               │       └── S0500.json\n        │               └── single\n        │                   ├── S0100.json\n        │                   ├── S0200.json\n        │                   ├── S0300.json\n        │                   ├── S0400.json\n        │                   └── S0500.json\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n        └── zenodo\n            ├── U0102__annotation.zip\n            ├── U0102__atr.zip\n            ├── U0102__kinect__2d-kpt.zip\n            ├── U0103__annotation.zip\n            ├── U0103__atr.zip\n            ├── U0103__kinect__2d-kpt.zip\n            ├── U0105__annotation.zip\n            ├── U0105__atr.zip\n            ├── U0105__kinect__2d-kpt.zip\n            ├── U0106__annotation.zip\n            ├── U0106__atr.zip\n            └── U0106__kinect__2d-kpt.zip\n```\n\n## License\n\nopenpack-toolkit has a MIT license, as found in the [LICENSE](./LICENCE) file.\n\nNOTE: [OpenPack Dataset](https://doi.org/10.5281/zenodo.5909086) itself is available under [Creative Commons Attribution Non Commercial Share Alike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode) license.\n',
    'author': 'Yoshimura Naoya',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://open-pack.github.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
