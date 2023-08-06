# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wfdb',
 'wfdb.io',
 'wfdb.io.convert',
 'wfdb.io.core',
 'wfdb.plot',
 'wfdb.processing']

package_data = \
{'': ['*']}

install_requires = \
['SoundFile>=0.10.0,<0.12.0',
 'matplotlib>=3.2.2,<4.0.0',
 'numpy>=1.10.1,<2.0.0',
 'pandas>=1.0.0,<2.0.0',
 'requests>=2.8.1,<3.0.0',
 'scipy>=1.0.0,<2.0.0']

extras_require = \
{'dev': ['pytest>=7.1.1,<8.0.0',
         'pytest-xdist>=2.5.0,<3.0.0',
         'pylint>=2.13.7,<3.0.0',
         'black>=22.3.0,<23.0.0',
         'Sphinx>=4.5.0,<5.0.0']}

setup_kwargs = {
    'name': 'wfdb',
    'version': '4.0.0',
    'description': 'The WFDB Python package: tools for reading, writing, and processing physiologic signals and annotations.',
    'long_description': '# The WFDB Python Package\n\n![signals](https://raw.githubusercontent.com/MIT-LCP/wfdb-python/main/demo-img.png)\n\n[![tests workflow](https://github.com/MIT-LCP/wfdb-python/actions/workflows/run-tests.yml/badge.svg)](https://github.com/MIT-LCP/wfdb-python/actions?query=workflow%3Arun-tests+event%3Apush+branch%3Amain)\n[![PyPI Downloads](https://img.shields.io/pypi/dm/wfdb.svg?label=PyPI%20downloads)](https://pypi.org/project/wfdb/)\n[![PhysioNet Project](https://img.shields.io/badge/DOI-10.13026%2Fegpf--2788-blue)](https://doi.org/10.13026/egpf-2788)\n[![Supported Python Versions](https://img.shields.io/pypi/pyversions/wfdb.svg)](https://pypi.org/project/wfdb)\n\n## Introduction\n\nA Python-native package for reading, writing, processing, and plotting physiologic signal and annotation data. The core I/O functionality is based on the Waveform Database (WFDB) [specifications](https://github.com/wfdb/wfdb-spec/).\n\nThis package is heavily inspired by the original [WFDB Software Package](https://www.physionet.org/content/wfdb/), and initially aimed to replicate many of its command-line APIs. However, the projects are independent, and there is no promise of consistency between the two, beyond each package adhering to the core specifications.\n\n## Documentation and Usage\n\nSee the [documentation site](http://wfdb.readthedocs.io) for the public APIs.\n\nSee the [demo.ipynb](https://github.com/MIT-LCP/wfdb-python/blob/main/demo.ipynb) notebook file for example use cases.\n\n## Installation\n\nThe distribution is hosted on PyPI at: <https://pypi.python.org/pypi/wfdb/>. The package can be directly installed from PyPI using either pip or poetry:\n\n```sh\npip install wfdb\npoetry add wfdb\n```\n\nOn Linux systems, accessing _compressed_ WFDB signal files requires installing `libsndfile`, by running `sudo apt-get install libsndfile1` or `sudo yum install libsndfile`. Support for Apple M1 systems is a work in progess (see <https://github.com/bastibe/python-soundfile/issues/310> and <https://github.com/bastibe/python-soundfile/issues/325>).\n\nThe development version is hosted at: <https://github.com/MIT-LCP/wfdb-python>. This repository also contains demo scripts and example data. To install the development version, clone or download the repository, navigate to the base directory, and run:\n\n```sh\n# Without dev dependencies\npip install .\npoetry install\n\n# With dev dependencies\npip install ".[dev]"\npoetry install -E dev\n\n# Install the dependencies only\npoetry install -E dev --no-root\n```\n\nSee the [note](#package-management) below about dev dependencies.\n\n## Developing\n\nWe welcome community contributions in the form of pull requests. When contributing code, please ensure:\n\n- Documentation is provided. New functions and classes should have numpy/scipy style [docstrings](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt).\n- Unit tests are written for new features that are not covered by [existing tests](https://github.com/MIT-LCP/wfdb-python/tree/main/tests).\n- The code style is consistent with the project\'s formating standards.\n\nRun the formatter with:\n\n```sh\nblack .\n```\n\n### Package and Dependency Management\n\nThis project uses [poetry](https://python-poetry.org/docs/) for package management and distribution.\n\nDevelopment dependencies are specified as optional dependencies, and then added to the "dev" extra group in the [pyproject.toml](./pyproject.toml) file.\n\n```sh\n# Do NOT use: poetry add <somepackage> --dev\npoetry add --optional <somepackage>\n```\n\nThe `[tool.poetry.dev-dependencies]` attribute is NOT used because of a [limitation](https://github.com/python-poetry/poetry/issues/3514) that prevents these dependencies from being pip installable. Therefore, dev dependencies are not installed when purely running `poetry install`, and the `--no-dev` flag has no meaning in this project.\n\n### Creating Distributions\n\nMake sure the versions in [version.py](./wfdb/version.py) and [pyproject.toml](./pyproject.toml) are updated and kept in sync.\n\nIt may be useful to publish to testpypi and preview the changes before publishing to PyPi. However, the project dependencies likely will not be available when trying to install from there.\n\nSetup: configure access to repositories:\n\n```sh\n# Create an API token, then add it\npoetry config pypi-token.pypi <my-token>\n\n# For testpypi\npoetry config repositories.test-pypi https://test.pypi.org/legacy/\npoetry config pypi-token.test-pypi <my-testpypi-token>\n```\n\nTo build and upload a new distribution:\n\n```sh\npoetry build\n\npoetry publish -r test-pypi\npoetry publish\n```\n\n### Creating Documentation\n\nThe project\'s documentation is generated by [Sphinx](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html) using the content in the [docs](./docs) directory. The generated content is then hosted on readthedocs (RTD) at: <http://wfdb.readthedocs.io>\n\nTo manage the content on RTD, request yourself to be added to the [wfdb](https://readthedocs.org/projects/wfdb/) project. The project has already been configured to import content from the GitHub repository. Documentation for new releases should be automatically built and uploaded. See the [import guide](https://docs.readthedocs.io/en/stable/intro/import-guide.html) for more details.\n\nThere is some redundancy in specifying the Sphinx requirements between pyproject.toml and [docs/requirements.txt](./docs/requirements.txt), the latter of which is used by RTD. Make sure that the content is consistent across the two files.\n\nTo generate the HTML content locally, install the required dependencies and run from the `docs` directory:\n\n```sh\nmake html\n```\n\n### Tests\n\nRun tests using pytest:\n\n```sh\npytest\n# Distribute tests across multiple cores.\n# https://github.com/pytest-dev/pytest-xdist\npytest -n auto\n```\n\n## Citing\n\nWhen using this resource, please cite the software [publication](https://physionet.org/content/wfdb-python/) oh PhysioNet.\n',
    'author': 'The Laboratory for Computational Physiology',
    'author_email': 'contact@physionet.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MIT-LCP/wfdb-python/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
