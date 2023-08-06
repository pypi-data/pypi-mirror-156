# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['document_tools',
 'document_tools.documents',
 'document_tools.encoders',
 'tests',
 'tests.documents']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0',
 'datasets>=2.3.2,<3.0.0',
 'transformers>=4.20.0,<5.0.0']

extras_require = \
{'dev': ['tox>=3.25.0,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=4.0.1,<5.0.0',
         'pre-commit>=2.19.0,<3.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0',
         'pytesseract>=0.3.9,<0.4.0',
         'ipykernel>=6.15.0,<7.0.0'],
 'doc': ['mkdocs>=1.3.0,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=8.3.6,<9.0.0',
         'mkdocstrings[python]>=0.19.0,<0.20.0',
         'mkdocs-autorefs>=0.4.1,<0.5.0',
         'Jinja2==3.0.3'],
 'test': ['black==22.3.0',
          'isort>=5.10.1,<6.0.0',
          'flake8>=3.9.2,<4.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'mypy>=0.961,<0.962',
          'pytest>=7.1.2,<8.0.0',
          'pytest-cov>=3.0.0,<4.0.0',
          'pytesseract>=0.3.9,<0.4.0']}

setup_kwargs = {
    'name': 'document-tools',
    'version': '0.1.1',
    'description': '🔧 Tools to automate your document understanding tasks.',
    'long_description': '# Document Tools\n\n\n[![pypi](https://img.shields.io/pypi/v/document-tools.svg)](https://pypi.org/project/document-tools/)\n[![python](https://img.shields.io/pypi/pyversions/document-tools.svg)](https://pypi.org/project/document-tools/)\n[![Build Status](https://github.com/deeptools-ai/document-tools/actions/workflows/dev.yml/badge.svg)](https://github.com/deeptools-ai/document-tools/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/deeptools-ai/document-tools/branch/main/graphs/badge.svg)](https://codecov.io/github/deeptools-ai/document-tools)\n\n\n\n🔧 Tools to automate your document understanding tasks.\n\nThis package contains tools to automate your document understanding tasks by leveraging the power of\n[🤗 Datasets](https://github.com/huggingface/datasets) and [🤗 Transformers](https://github.com/huggingface/transformers).\n\nWith this package, you can (or will be able to):\n\n- 🚧 **Create** a dataset from a collection of documents.\n- ✅ **Transform** a dataset to a format that is suitable for training a model.\n- 🚧 **Train** a model on a dataset.\n- 🚧 **Evaluate** the performance of a model on a dataset of documents.\n- 🚧 **Export** a model to a format that is suitable for inference.\n\n\n## Features\n\nThis project is under development and is in the alpha stage. It is not ready for production use, and if you find any\nbugs or have any suggestions, please let us know by opening an [issue](https://github.com/deeptools-ai/document-tools/issues)\nor a [pull request](https://github.com/deeptools-ai/document-tools/pulls).\n\n### Featured models\n\n- [ ] [DiT](https://huggingface.co/docs/transformers/model_doc/dit)\n- [x] [LayoutLMv2](https://huggingface.co/docs/transformers/model_doc/layoutlmv2)\n- [x] [LayoutLMv3](https://huggingface.co/docs/transformers/model_doc/layoutlmv3)\n- [ ] [LayoutXLM](https://huggingface.co/docs/transformers/model_doc/layoutxlm)\n\n## Usage\n\nOne-liner to get started:\n\n```python\nfrom datasets import load_dataset\nfrom document_tools import tokenize_dataset\n\n# Load a dataset from 🤗 Hub\ndataset = load_dataset("deeptools-ai/test-document-invoice", split="train")\n\n# Tokenize the dataset\ntokenized_dataset = tokenize_dataset(dataset, target_model="layoutlmv3")\n```\n\nFor more information, please see the [documentation](https://deeptools-ai.github.io/document-tools/)\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n',
    'author': 'deeptools.ai',
    'author_email': 'contact@deeptools.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/deeptools-ai/document-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
