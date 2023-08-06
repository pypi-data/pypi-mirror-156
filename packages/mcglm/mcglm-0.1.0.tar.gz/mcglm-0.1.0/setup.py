# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mcglm']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.2,<4.0.0',
 'numpy==1.19.5',
 'pandas>=1.3.3,<2.0.0',
 'patsy>=0.5.2,<0.6.0',
 'scipy==1.7.1',
 'seaborn>=0.11.2,<0.12.0',
 'statsmodels>=0.13.2,<0.14.0']

setup_kwargs = {
    'name': 'mcglm',
    'version': '0.1.0',
    'description': 'Multivariate Covariance Generalized Linear Models',
    'long_description': None,
    'author': 'Jean Carlos Maia',
    'author_email': 'jeanclmaia@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
