# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gwdc_python',
 'gwdc_python.files',
 'gwdc_python.files.tests',
 'gwdc_python.jobs',
 'gwdc_python.jobs.tests',
 'gwdc_python.tests',
 'gwdc_python.utils',
 'gwdc_python.utils.tests']

package_data = \
{'': ['*']}

install_requires = \
['importlib-metadata>=4.5.0,<5.0.0',
 'jwt>=1.2.0,<2.0.0',
 'pyhumps>=3.7.1,<4.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.25.1,<3.0.0',
 'tqdm>=4.61.2,<5.0.0']

extras_require = \
{'docs': ['Sphinx>=4.0.2,<5.0.0', 'sphinx-rtd-theme>=0.5.2,<0.6.0']}

setup_kwargs = {
    'name': 'gwdc-python',
    'version': '0.4.1',
    'description': 'API for GWDC modules',
    'long_description': 'GWDC Python API\n===============\n\nThis package handles requests for the GWDC modules. Presently, it primarily handles the requests for `gwcloud-python <https://pypi.org/project/gwcloud-python/>`_.',
    'author': 'Thomas Reichardt',
    'author_email': 'treichardt@swin.edu.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gravitationalwavedc/gwdc_python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
