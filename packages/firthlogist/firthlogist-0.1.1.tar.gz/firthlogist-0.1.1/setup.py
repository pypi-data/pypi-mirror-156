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
    'version': '0.1.1',
    'description': "Python implementation of Logistic Regression with Firth's bias reduction",
    'long_description': "# firthlogist\n\n[![PyPI](https://img.shields.io/pypi/v/firthlogist.svg)](https://pypi.org/project/firthlogist/)\n[![GitHub](https://img.shields.io/github/license/jzluo/firthlogist)](https://github.com/jzluo/firthlogist/blob/master/LICENSE)\n\nA Python implementation of Logistic Regression with Firth's bias reduction.\n\nWIP!\n\n## Installation\n    pip install firthlogist\n\n## Usage\nfirthlogist follows the sklearn API.\n\n```python\nfrom firthlogist import FirthLogisticRegression\n\nfirth = FirthLogisticRegression()\nfirth.fit(X, y)\ncoefs = firth.coef_\npvals = firth.pvals_\nbse = firth.bse_\n```\n\n### Parameters\n\n`max_iter`: **_int_, default=25**\n\n&emsp;The maximum number of Newton-Raphson iterations.\n\n`max_halfstep`: **_int_, default=1000**\n\n&emsp;The maximum number of step-halvings in one Newton-Raphson iteration.\n\n`max_stepsize`: **_int_, default=5**\n\n&emsp;The maximum step size - for each coefficient, the step size is forced to\nbe less than max_stepsize.\n\n`tol`: **_float_, default=0.0001**\n\n&emsp;Convergence tolerance for stopping.\n\n`fit_intercept`: **_bool_, default=True**\n\n&emsp;Specifies if intercept should be added.\n\n`skip_lrt`: **_bool_, default=False**\n\n&emsp;If True, p-values will not be calculated. Calculating the p-values can\nbe expensive since the fitting procedure is repeated for each\ncoefficient.\n\n\n### Attributes\n`bse_`\n\n&emsp;Standard errors of the coefficients.\n\n`classes_`\n\n&emsp;A list of the class labels.\n\n`coef_`\n\n&emsp;The coefficients of the features.\n\n`intercept_`\n\n&emsp;Fitted intercept. If `fit_intercept = False`, the intercept is set to zero.\n\n`n_iter_`\n\n&emsp;Number of Newton-Raphson iterations performed.\n\n`pvals_`\n\n&emsp;p-values calculated by penalized likelihood ratio tests.\n\n## References\nFirth, D (1993). Bias reduction of maximum likelihood estimates.\n*Biometrika* 80, 27–38.\n\nHeinze G, Schemper M (2002). A solution to the problem of separation in logistic\nregression. *Statistics in Medicine* 21: 2409-2419.\n",
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
