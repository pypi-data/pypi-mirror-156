# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['recorpy', 'recorpy.test']

package_data = \
{'': ['*'],
 'recorpy': ['.pytest_cache/*', '.pytest_cache/v/cache/*'],
 'recorpy.test': ['.pytest_cache/*', '.pytest_cache/v/cache/*']}

install_requires = \
['numpy>=1.23.0,<2.0.0', 'pandas>=1.4.3,<2.0.0', 'scikit-learn>=1.1.1,<2.0.0']

setup_kwargs = {
    'name': 'recorpy',
    'version': '0.1.5',
    'description': 'ReCorPy is a small package to reorder correlation matrices from dataframes for better visualizations',
    'long_description': '\n<p align="center">\n  <img src="https://raw.githubusercontent.com/thebooort/ReCorPy/main/assets/logo.png">\n</p>\n<h2 align="center">ReCorPy</h2>\n\n> A python\'s package for reordering/clustering correlation matrices\n\n[![Documentation Status](https://readthedocs.org/projects/recorpy/badge/?version=latest)](https://recorpy.readthedocs.io/en/latest/?badge=latest)\n[![PyPI Version][pypi-image]][pypi-url]\n[![Build Status][build-image]][build-url]\n[![Coverage Status](https://coveralls.io/repos/github/thebooort/ReCorPy/badge.svg?branch=main)](https://coveralls.io/github/thebooort/ReCorPy?branch=main)\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n\n`recorpy` reorder correlation matrixes to get better visual analysis. All it is made with the original dataframe. And the result\nis a new dataframe with columns reordered, to let you re-use it wherever you want.\n\nInput parameters:\n\n-   _method_ - \n-   _model_ - , default: \n-   _cluster_ - , default: \n\n\n## Installation\n\n```sh\npip install recorpy\n```\n\n## Usage\n\n\n```python\n        >>> df = pd.DataFrame(np.random.rand(3,3))\n        >>> ReorderCorr(df)\n```\n\n## Development setup\n\n```sh\n$ python3 -m venv env\n$ . env/bin/activate\n$ make deps\n$ tox\n```\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nMake sure to add or update tests as appropriate.\n\nUse [Black](https://black.readthedocs.io/en/stable/) for code formatting and [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.4/) for commit messages.\n\n## [Changelog](CHANGELOG.md)\n\n## License\n\n[GPL](https://choosealicense.com/licenses/gpl/)\n\n<!-- Badges -->\n\n[pypi-image]: https://img.shields.io/pypi/v/recorpy\n[pypi-url]: https://pypi.org/project/recorpy/\n[build-image]: https://github.com/thebooort/recorpy/actions/workflows/python-app.yml/badge.svg\n[build-url]: https://github.com/thebooort/recorpy/actions/workflows/python-app.yml\n[coverage-image]: https://codecov.io/gh/thebooort/recorpy/branch/main/graph/badge.svg\n[coverage-url]: https://codecov.io/gh/thebooort/recorpy\n[quality-image]: https://api.codeclimate.com/v1/badges/3130fa0ba3b7993fbf0a/maintainability\n[quality-url]: https://codeclimate.com/github/thebooort/recorpy\n\n',
    'author': 'thebooort',
    'author_email': '18428931+thebooort@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thebooort/ReCorPy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
