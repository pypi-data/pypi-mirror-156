# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['physiocurve',
 'physiocurve.common',
 'physiocurve.ecg',
 'physiocurve.flow',
 'physiocurve.pandas',
 'physiocurve.ppg',
 'physiocurve.pressure',
 'physiocurve.pressure.reference']

package_data = \
{'': ['*']}

install_requires = \
['neurokit2>=0.2.0,<0.3.0',
 'numba>=0.55.2,<0.56.0',
 'pandas>=1.4.3,<2.0.0',
 'scipy>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'physiocurve',
    'version': '2022.6.26',
    'description': 'Analyse biometric time series',
    'long_description': '# physiocurve\nphysiocurve is a library to analyze biometric time series such as ECG and pulse waves, often obtained from patient monitors.\n',
    'author': 'Jona Joachim',
    'author_email': 'jona@joachim.cc',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://framagit.org/jaj/physiocurve',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
