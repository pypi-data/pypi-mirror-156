# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zoish', 'zoish.feature_selectors', 'zoish.notebooks', 'zoish.utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'fasttreeshap>=0.1.2,<0.2.0',
 'feature-engine>=1.4.1,<2.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'numba>=0.55.2,<0.56.0',
 'numpy<1.22.0',
 'optuna>=2.10.1,<3.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pip-licenses>=3.5.4,<4.0.0',
 'scikit-learn>=1.1.1,<2.0.0',
 'scipy>=1.8.1,<2.0.0',
 'shap>=0.41.0,<0.42.0',
 'xgboost>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'zoish',
    'version': '0.1.3',
    'description': 'This project uses shapely values for selecting Top n features compatible with scikit learn pipeline',
    'long_description': None,
    'author': 'drhosseinjavedani',
    'author_email': 'h.javedani@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/drhosseinjavedani/zoish',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
