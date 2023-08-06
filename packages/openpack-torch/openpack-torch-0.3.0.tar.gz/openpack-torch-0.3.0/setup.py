# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openpack_torch',
 'openpack_torch.configs',
 'openpack_torch.data',
 'openpack_torch.models',
 'openpack_torch.models.imu',
 'openpack_torch.models.keypoint']

package_data = \
{'': ['*']}

install_requires = \
['hydra-core>=1.2.0,<2.0.0',
 'numpy<1.22.0',
 'omegaconf>=2.2.1,<3.0.0',
 'openpack-toolkit>=0.4.0,<0.5.0',
 'pandas>=1.2.4,<2.0.0',
 'pytorch-lightning>=1.6.3,<2.0.0',
 'sklearn>=0.0',
 'torch>=1.9.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'openpack-torch',
    'version': '0.3.0',
    'description': 'PyTorch extention to work around with OpenPack dataset',
    'long_description': '# openpack-torch\n\n[![Test](https://github.com/open-pack/openpack-torch/actions/workflows/test.yaml/badge.svg)](https://github.com/open-pack/openpack-torch/actions/workflows/test.yaml)\n[![GitHub Pages](https://github.com/open-pack/openpack-torch/actions/workflows/deploy-docs.yaml/badge.svg)](https://github.com/open-pack/openpack-torch/actions/workflows/deploy-docs.yaml)\n\nPyTorch utilities to work around with [OpenPack Dataset](https://open-pack.github.io/).\n\n## Setup\n\nYou can install via pip with the following command.\n\n```bash\n# Pip\npip install openpack-torch\n\n# Poetry\npoetry add  openpack-torch\n```\n\n## Docs\n\n- [Dataset Page](https://open-pack.github.io/)\n- [API Docs](https://open-pack.github.io/openpack-torch/openpack_torch)\n- [PyPI - openpack-torch](https://pypi.org/project/openpack-torch/)\n\n## Examples\n\n### Operation Recognition (Semantic Segmentation)\n\n#### IMU\n\n- Acceleration\n  - [U-Net](./examples/unet/)\n  - [DeepConvLSTM](./examples/deep-conv-lstm/)\n\n#### Vision\n\n- Keypoints\n  - [ST-GCN](./examples/st-gcn)\n\n#### Scores of Baseline Moodel (Preliminary Experiments)\n\n##### Split: Pilot Challenge\n\n| Model                    | F1 (Test Set) | F1 (Submission Set) | Date       | Code |\n|--------------------------|---------------|---------------------|------------|------|\n| UNet                     | 0.3451        | 0.3747              | 2022-06-28 | [main.py](./examples/unet/main.py) |\n| DeepConvLSTM             | 0.7081        | 0.7695              | 2022-06-28 | [main.py](./examples/deep-conv-lstm/main.py) |\n| DeepConvLSTM + Self-Attn | 0.8161        | 0.8409              | 2022-06-28 | [main.py](./examples/deep-conv-lstm/main_self_attention.py) |\n| ST-GCN                   | -             | -                   |            |      |\n\nNOTE: F1 = F1-measure (macro average)\n\n## LICENCE\n\nThis software (openpack-torch) is distributed under [MIT Licence](./LICENSE).\nFor the license of "OpenPack Dataset", please check [this site (https://open-pack.github.io/)](https://open-pack.github.io/).\n',
    'author': 'Yoshimura Naoya',
    'author_email': 'yoshimura.naoya@ist.osaka-u.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://open-pack.github.io/home',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.11,<3.10',
}


setup(**setup_kwargs)
