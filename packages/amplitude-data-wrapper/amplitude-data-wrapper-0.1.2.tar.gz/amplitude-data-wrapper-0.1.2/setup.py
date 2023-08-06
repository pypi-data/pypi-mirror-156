# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['amplitude_data_wrapper']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0', 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'amplitude-data-wrapper',
    'version': '0.1.2',
    'description': 'python wrapper for using the amplitude analytics and taxonomy APIs',
    'long_description': None,
    'author': 'Tobias McVey',
    'author_email': 'tobias.mcvey@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
