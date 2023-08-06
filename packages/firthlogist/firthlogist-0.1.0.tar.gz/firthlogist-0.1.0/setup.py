# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['firthlogist', 'firthlogist.tests']

package_data = \
{'': ['*'], 'firthlogist': ['.pytest_cache/*', '.pytest_cache/v/cache/*']}

install_requires = \
['numpy>=1.22.4,<2.0.0',
 'pandas>=1.4.2,<2.0.0',
 'pytest>=7.1.2,<8.0.0',
 'scikit-learn>=1.1.1,<2.0.0']

setup_kwargs = {
    'name': 'firthlogist',
    'version': '0.1.0',
    'description': "Python implementation of Logistic Regression with Firth's bias reduction",
    'long_description': "# firthlogist\n\n[![PyPI](https://img.shields.io/pypi/v/firthlogist.svg)](https://pypi.org/project/firthlogist/)\n[![GitHub](https://img.shields.io/github/license/jzluo/firthlogist)](https://github.com/jzluo/firthlogist/blob/master/LICENSE)\n\nA Python implementation of Logistic Regression with Firth's bias reduction.\n\nWIP!\n\n## Installation\n    pip install firthlogist\n\n## Usage\nfirthlogist follows the sklearn API.\n\n```python\nfrom firthlogist import FirthLogisticRegression\n\nfirth = FirthLogisticRegression()\nfirth.fit(X, y)\ncoefs = firth.coef_\npvals = firth.pvals_\nbse = firth.bse_\n```\n\n## References\nFirth, D (1993). Bias reduction of maximum likelihood estimates.\n*Biometrika* 80, 27–38.\n\nHeinze G, Schemper M (2002). A solution to the problem of separation in logistic\nregression. *Statistics in Medicine* 21: 2409-2419.\n",
    'author': 'Jon Luo',
    'author_email': 'jzluo@alumni.cmu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jzluo/firthlogist',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
